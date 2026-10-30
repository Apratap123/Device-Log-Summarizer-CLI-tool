import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

class DeviceLogSummarizer:
    def __init__(self, max_temp_threshold: float = 80.0):
        self.max_temp_threshold = max_temp_threshold

    def parse_csv(self, file_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source telemetry file not found: {file_path}")

        records: List[Dict[str, Any]] = []
        with open(file_path, mode="r", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                return records

            required_fields = {"device_id", "status", "temperature"}
            normalized_fieldnames = {field.strip().lower(): field for field in reader.fieldnames if field}
            
            if not required_fields.issubset(normalized_fieldnames.keys()):
                raise ValueError(
                    f"CSV missing mandatory columns. Required: {required_fields}, Found: {list(reader.fieldnames)}"
                )

            id_col = normalized_fieldnames["device_id"]
            status_col = normalized_fieldnames["status"]
            temp_col = normalized_fieldnames["temperature"]

            for row_index, row in enumerate(reader, start=2):
                raw_device_id = row.get(id_col)
                raw_status = row.get(status_col)
                raw_temp = row.get(temp_col)

                if raw_device_id is None or raw_status is None or raw_temp is None:
                    continue

                device_id = raw_device_id.strip()
                status = raw_status.strip().upper()
                
                if not device_id:
                    continue

                try:
                    temperature = float(raw_temp.strip())
                except (ValueError, TypeError):
                    continue

                records.append({
                    "device_id": device_id,
                    "status": status,
                    "temperature": temperature
                })

        return records

    def aggregate_and_filter(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped_data: Dict[str, Dict[str, Any]] = {}

        for record in records:
            dev_id = record["device_id"]
            if dev_id not in grouped_data:
                grouped_data[dev_id] = {
                    "device_id": dev_id,
                    "total_records": 0,
                    "temperature_sum": 0.0,
                    "error_count": 0
                }

            grouped_data[dev_id]["total_records"] += 1
            grouped_data[dev_id]["temperature_sum"] += record["temperature"]
            if record["status"] == "ERROR":
                grouped_data[dev_id]["error_count"] += 1

        summary_results: List[Dict[str, Any]] = []
        for dev_id, data in grouped_data.items():
            total = data["total_records"]
            avg_temp = round(data["temperature_sum"] / total, 2) if total > 0 else 0.0

            if avg_temp <= self.max_temp_threshold:
                summary_results.append({
                    "device_id": dev_id,
                    "total_records": total,
                    "average_temperature": avg_temp,
                    "error_count": data["error_count"]
                })

        summary_results.sort(key=lambda item: item["device_id"])
        return summary_results

    def export_json(self, data: List[Dict[str, Any]], output_path: str) -> None:
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(output_path, mode="w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)

    def print_summary_table(self, data: List[Dict[str, Any]]) -> None:
        if not data:
            print("\nNo devices met the criteria (all filtered out or no data provided).\n")
            return

        header_dev = "Device ID"
        header_total = "Total Records"
        header_avg = "Avg Temp (C)"
        header_err = "Error Count"

        col_w_dev = max(len(header_dev), max(len(str(d["device_id"])) for d in data)) + 4
        col_w_total = max(len(header_total), max(len(str(d["total_records"])) for d in data)) + 4
        col_w_avg = max(len(header_avg), max(len(f"{d['average_temperature']:.2f}") for d in data)) + 4
        col_w_err = max(len(header_err), max(len(str(d["error_count"])) for d in data)) + 4

        divider = "+" + "-" * col_w_dev + "+" + "-" * col_w_total + "+" + "-" * col_w_avg + "+" + "-" * col_w_err + "+"
        header_row = f"| {header_dev.ljust(col_w_dev - 2)} | {header_total.ljust(col_w_total - 2)} | {header_avg.ljust(col_w_avg - 2)} | {header_err.ljust(col_w_err - 2)} |"

        print("\n" + "=" * len(divider))
        print(" DEVICE TELEMETRY SUMMARY REPORT ".center(len(divider)))
        print(f" (Devices with Avg Temp <= {self.max_temp_threshold} C) ".center(len(divider)))
        print("=" * len(divider))
        print(divider)
        print(header_row)
        print(divider)

        for row in data:
            dev_str = str(row["device_id"]).ljust(col_w_dev - 2)
            total_str = str(row["total_records"]).rjust(col_w_total - 2)
            avg_str = f"{row['average_temperature']:.2f}".rjust(col_w_avg - 2)
            err_str = str(row["error_count"]).rjust(col_w_err - 2)
            print(f"| {dev_str} | {total_str} | {avg_str} | {err_str} |")

        print(divider + "\n")

    def run(self, input_csv: str, output_json: str) -> List[Dict[str, Any]]:
        raw_records = self.parse_csv(input_csv)
        summary = self.aggregate_and_filter(raw_records)
        self.export_json(summary, output_json)
        self.print_summary_table(summary)
        return summary

def main() -> None:
    parser = argparse.ArgumentParser(description="Device Log Summarizer CLI Tool")
    parser.add_argument("--input", "-i", default="device_telemetry.csv", help="Path to input CSV file")
    parser.add_argument("--output", "-o", default="device_summary.json", help="Path to output JSON file")
    parser.add_argument("--threshold", "-t", type=float, default=80.0, help="Maximum average temperature threshold")

    args = parser.parse_args()

    try:
        summarizer = DeviceLogSummarizer(max_temp_threshold=args.threshold)
        summarizer.run(input_csv=args.input, output_json=args.output)
        print(f"Summary successfully exported to: {os.path.abspath(args.output)}")
    except FileNotFoundError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Unexpected processing error: {err}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
