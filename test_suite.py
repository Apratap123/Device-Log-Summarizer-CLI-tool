import json
import os
import tempfile
import unittest
from sensor_sanitizer import clean_sensor_readings
from log_summarizer import DeviceLogSummarizer
from chart_generator import generate_temperature_chart

class TestSensorSanitizer(unittest.TestCase):
    def test_mixed_inputs_and_clipping(self):
        inputs = ["12.5", None, -5, "sensor_error", 620.4, 0, 499.9, "350.25", True, False]
        expected = [12.5, 500.0, 0.0, 499.9, 350.25]
        self.assertEqual(clean_sensor_readings(inputs), expected)

    def test_empty_input(self):
        self.assertEqual(clean_sensor_readings([]), [])

    def test_non_list_input(self):
        self.assertEqual(clean_sensor_readings(None), [])
        self.assertEqual(clean_sensor_readings("invalid_string"), [])
        self.assertEqual(clean_sensor_readings(123), [])

    def test_all_invalid_entries(self):
        inputs = [None, "fault", -10.5, "N/A", -0.001, False, True]
        self.assertEqual(clean_sensor_readings(inputs), [])

    def test_boundary_clipping(self):
        inputs = [0.0, 499.999, 500.0, 500.001, 10000.0]
        expected = [0.0, 499.999, 500.0, 500.0, 500.0]
        self.assertEqual(clean_sensor_readings(inputs), expected)

    def test_scientific_notation(self):
        inputs = ["1e2", "5.5e1", 1e3]
        expected = [100.0, 55.0, 500.0]
        self.assertEqual(clean_sensor_readings(inputs), expected)

class TestDeviceLogSummarizer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.valid_csv_path = os.path.join(self.temp_dir.name, "telemetry.csv")
        self.output_json_path = os.path.join(self.temp_dir.name, "summary.json")

        csv_content = (
            "device_id,status,temperature\n"
            "DEV_A,ACTIVE,40.0\n"
            "DEV_A,WARNING,50.0\n"
            "DEV_A,ERROR,60.0\n"
            "DEV_B,ACTIVE,90.0\n"
            "DEV_B,WARNING,92.0\n"
            "DEV_C,ACTIVE,25.0\n"
            "DEV_C,ACTIVE,35.0\n"
        )
        with open(self.valid_csv_path, mode="w", encoding="utf-8") as f:
            f.write(csv_content)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_aggregation_and_filtering(self):
        summarizer = DeviceLogSummarizer(max_temp_threshold=80.0)
        results = summarizer.run(self.valid_csv_path, self.output_json_path)

        dev_ids = [r["device_id"] for r in results]
        self.assertIn("DEV_A", dev_ids)
        self.assertIn("DEV_C", dev_ids)
        self.assertNotIn("DEV_B", dev_ids)

        dev_a = next(r for r in results if r["device_id"] == "DEV_A")
        self.assertEqual(dev_a["total_records"], 3)
        self.assertEqual(dev_a["average_temperature"], 50.0)
        self.assertEqual(dev_a["error_count"], 1)

        dev_c = next(r for r in results if r["device_id"] == "DEV_C")
        self.assertEqual(dev_c["total_records"], 2)
        self.assertEqual(dev_c["average_temperature"], 30.0)
        self.assertEqual(dev_c["error_count"], 0)

        self.assertTrue(os.path.exists(self.output_json_path))
        with open(self.output_json_path, mode="r", encoding="utf-8") as f:
            exported_data = json.load(f)
        self.assertEqual(len(exported_data), 2)

    def test_missing_file_raises_exception(self):
        summarizer = DeviceLogSummarizer()
        with self.assertRaises(FileNotFoundError):
            summarizer.parse_csv("non_existent_file.csv")

    def test_malformed_rows_graceful_handling(self):
        corrupt_csv_path = os.path.join(self.temp_dir.name, "corrupt.csv")
        content = (
            "device_id,status,temperature\n"
            "DEV_1,ACTIVE,45.0\n"
            "DEV_1,ERROR,bad_temp\n"
            ",ACTIVE,55.0\n"
            "DEV_1,ACTIVE,55.0\n"
        )
        with open(corrupt_csv_path, mode="w", encoding="utf-8") as f:
            f.write(content)

        summarizer = DeviceLogSummarizer()
        records = summarizer.parse_csv(corrupt_csv_path)
        self.assertEqual(len(records), 2)
        summary = summarizer.aggregate_and_filter(records)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["device_id"], "DEV_1")
        self.assertEqual(summary[0]["total_records"], 2)
        self.assertEqual(summary[0]["average_temperature"], 50.0)

    def test_missing_column_headers(self):
        invalid_header_csv = os.path.join(self.temp_dir.name, "bad_headers.csv")
        with open(invalid_header_csv, mode="w", encoding="utf-8") as f:
            f.write("wrong_col1,wrong_col2\n1,2\n")

        summarizer = DeviceLogSummarizer()
        with self.assertRaises(ValueError):
            summarizer.parse_csv(invalid_header_csv)

class TestChartGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.json_path = os.path.join(self.temp_dir.name, "test_summary.json")
        self.chart_path = os.path.join(self.temp_dir.name, "test_chart.png")

        data = [
            {"device_id": "DEV_A", "total_records": 5, "average_temperature": 45.2, "error_count": 0},
            {"device_id": "DEV_B", "total_records": 5, "average_temperature": 71.0, "error_count": 2}
        ]
        with open(self.json_path, mode="w", encoding="utf-8") as f:
            json.dump(data, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_chart_creation(self):
        generate_temperature_chart(self.json_path, self.chart_path)
        self.assertTrue(os.path.exists(self.chart_path))
        self.assertGreater(os.path.getsize(self.chart_path), 1000)

if __name__ == "__main__":
    unittest.main()
