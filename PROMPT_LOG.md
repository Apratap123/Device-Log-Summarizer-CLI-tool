# AI Interaction & Prompting Log (`PROMPT_LOG.md`)

This log details the AI-assisted generation and refinement process for the **Section 3: AI Prompting & Charting Challenge** as part of the Software Engineering Intern Technical Assessment.

---

## 1. Initial Prompt to the AI

### Prompt Provided:
```text
Write a clean, standalone Python script using matplotlib that loads an aggregated JSON file named 'device_summary.json' (containing objects with keys: device_id, total_records, average_temperature, error_count) and generates a bar chart comparing the average temperature per device. Save the resulting figure as 'device_temperature_chart.png'. Ensure the code has no comments and runs directly from terminal.
```

---

## 2. AI First Attempt Output & Identified Bugs / Formatting Mistakes

### Initial Code Produced by AI:
```python
import json
import matplotlib.pyplot as plt

with open('device_summary.json', 'r') as f:
    data = json.load(f)

devices = [d['device_id'] for d in data]
temps = [d['average_temperature'] for d in data]

plt.bar(devices, temps)
plt.title('Device Temperature')
plt.xlabel('Device')
plt.ylabel('Temp')
plt.savefig('device_temperature_chart.png')
```

### Issues and Defects Identified in First Attempt:
1. **Label Overlap & Missing Padding**:
   - The device identifiers along the x-axis overlapped with each other and collided with the x-axis border because neither layout adjustments (`tight_layout()`), explicit figure sizing, nor category padding were configured.
2. **Missing Reference Threshold**:
   - The assessment requirements specified filtering devices above `80.0°C`. The initial chart lacked any visual indicator or threshold line showing the operational cutoff limit (`80.0°C`), reducing the analytical value of the chart.
3. **No Metric Annotations on Bars**:
   - The bars did not display exact values on top, forcing viewers to squint at the y-axis ticks.
4. **No Status Distinction / Color Differentiation**:
   - All bars were rendered in a single default flat blue without visual distinction between healthy devices (0 errors) and faulty devices (devices containing error records).
5. **Lack of Error Handling & CLI Arguments**:
   - The script crashed with an unhandled exception if `device_summary.json` was missing or contained empty records.

---

## 3. Follow-up Prompt Used to Fix the Issues

### Prompt Provided:
```text
Refine the script with the following fixes:
1. Fix all layout and overlapping issues by explicitly setting figure size (9x6 inches at 300 DPI) and calling plt.tight_layout().
2. Add a horizontal dashed reference line at y = 80.0 to clearly indicate the maximum allowed temperature threshold limit.
3. Differentiate bar colors based on error status: use a solid slate blue (#2b5c8f) for devices with 0 errors, and coral red (#d9534f) for devices that encountered errors, with an explanatory legend.
4. Add clear numerical value annotations directly on top of each bar displaying the exact average temperature and the error count.
5. Expand the y-axis limit appropriately so bar annotations never clip outside the plotting area.
6. Make the script robust: add CLI arguments (--input, --output) with argparse and handle missing/empty JSON files gracefully without crashing.
7. Do not include any code comments in the Python code.
```

---

## 4. Final Result & Verification

- **Final Script**: [chart_generator.py](file:///c:/Users/anujr/Downloads/TAsk/chart_generator.py)
- **Generated Visualization**: [device_temperature_chart.png](file:///c:/Users/anujr/Downloads/TAsk/device_temperature_chart.png)
- **Verification**: The generated chart renders cleanly with distinct colors for healthy vs. errored devices, high-resolution rendering (300 DPI), zero label collisions, numerical labels on every bar, and an explicit reference threshold at 80.0°C.
