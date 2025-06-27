import json
import csv

# Files to convert
input_files = [
    ("cleaned_merged_topics.json", "merged_output.csv"),
    ("cleaned_file_topics.json", "file_output.csv")
]

for json_file, csv_file in input_files:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Define column headers
    fieldnames = ["key", "label", "input", "output"]

    with open(csv_file, "w", encoding="utf-8", newline="") as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            writer.writerow({
                "key": item.get("key", ""),
                "label": item.get("label", ""),
                "input": item.get("input", ""),
                "output": item.get("output", "")
            })

    print(f"✅ Converted {json_file} to {csv_file}")
