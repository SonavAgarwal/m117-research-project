import json
import csv
import os

# File paths
json_folder_path = "cves" 
csv_file_path = "output.csv"

# Load all JSON files from the folder
# Map each file_name to data
data = {}
for file_name in os.listdir(json_folder_path):
    path = f"{json_folder_path}/{file_name}"
    with open(path, "r") as json_file:
        data[file_name] = json.load(json_file)
print(data)

# Convert JSON to CSV
with open(csv_file_path, "w", newline="") as csvfile:
    # Define CSV headers
    fieldnames = [
        "cveId",
        "dateReported",
        "vulnerabilityType",
        "language",
        "fixes",
        "severity",
        "component"
    ]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for file_name in data:
        entry = data[file_name]

        # Unpack JSON fields into a flat structure
        row = {
            "cveId" : entry["cveId"],
            "dateReported" : entry["dateReported"],
            "vulnerabilityType" : entry["vulnerabilityType"],
            "language" : entry["language"],
            "fixes" : entry["fixes"],
            "severity" : entry["severity"],
            "component" : entry["component"]
        }
        writer.writerow(row)

print(f"CSV file has been created: {os.path.abspath(csv_file_path)}")
