import argparse
import json
import os
import sys
# pyrefly: ignore[missing-import]
import matplotlib.pyplot as plt

def generate_temperature_chart(json_path: str, output_image_path: str) -> None:
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Input JSON file not found: {json_path}")

    with open(json_path, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    if not data or not isinstance(data, list):
        print("Warning: JSON dataset is empty or invalid. Chart generation skipped.", file=sys.stderr)
        return

    device_ids = [item.get("device_id", "Unknown") for item in data]
    avg_temps = [float(item.get("average_temperature", 0.0)) for item in data]
    error_counts = [int(item.get("error_count", 0)) for item in data]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

    bar_colors = ["#2b5c8f" if err == 0 else "#d9534f" for err in error_counts]
    bars = ax.bar(device_ids, avg_temps, color=bar_colors, width=0.55, edgecolor="#1c3b5e", linewidth=1.2, zorder=3)

    ax.axhline(y=80.0, color="#b22222", linestyle="--", linewidth=1.5, alpha=0.8, zorder=2, label="Threshold (80.0°C)")

    ax.set_title("Average Temperature per Device (Telemetric Summary)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Device Identifier", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_ylabel("Average Temperature (°C)", fontsize=11, fontweight="bold", labelpad=10)

    max_temp = max(avg_temps) if avg_temps else 80.0
    y_upper_limit = max(90.0, max_temp + 12.0)
    ax.set_ylim(0, y_upper_limit)

    for bar, temp, err in zip(bars, avg_temps, error_counts):
        height = bar.get_height()
        annotation_text = f"{temp:.2f}°C" if err == 0 else f"{temp:.2f}°C\n({err} err)"
        ax.annotate(
            annotation_text,
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold"
        )

    ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=10)
    ax.tick_params(axis="y", labelsize=10)

    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor="#2b5c8f", edgecolor="#1c3b5e", label="Normal Device (0 errors)"),
        plt.Rectangle((0, 0), 1, 1, facecolor="#d9534f", edgecolor="#1c3b5e", label="Device with Errors"),
        plt.Line2D([0], [0], color="#b22222", linestyle="--", linewidth=1.5, label="Threshold Limit (80°C)")
    ]
    ax.legend(handles=legend_elements, loc="upper right", framealpha=0.9)

    plt.tight_layout()

    out_dir = os.path.dirname(output_image_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    plt.savefig(output_image_path, dpi=300)
    plt.close(fig)
    print(f"Chart successfully saved to: {os.path.abspath(output_image_path)}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Device Temperature Visualization Generator")
    parser.add_argument("--input", "-i", default="device_summary.json", help="Path to aggregated JSON file")
    parser.add_argument("--output", "-o", default="device_temperature_chart.png", help="Path to destination chart image")

    args = parser.parse_args()

    try:
        generate_temperature_chart(json_path=args.input, output_image_path=args.output)
    except Exception as err:
        print(f"Visualization Error: {err}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
