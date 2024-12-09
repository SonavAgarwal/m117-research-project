import json
import csv
import os
from urllib.parse import urlparse
from collections import defaultdict
import re
import requests

# File paths
json_folder_path = "cves" 
csv_file_path = "output.csv"
csv_commit_path = "commits.csv"

# Regex for matching commit ids in URLs
regex = r'\b([0-9a-fA-F]{40})\b'

# Load all JSON files from the folder
# Map each file_name to data
data = {}
for file_name in os.listdir(json_folder_path):
    path = f"{json_folder_path}/{file_name}"
    with open(path, "r") as json_file:
        data[file_name] = json.load(json_file)

# Map each file_name (CVE ID) to commit data
commit_data = defaultdict(list)
version_control_platforms = set()
vc_vulnerability_count = defaultdict(int)

removed_commits = 0
removed_rows = 0

gerrit_commits = []

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
        "component",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for file_name in data:
        entry = data[file_name]

        # collect fix/commit data
        for fix in entry["fixes"]:
            parsed_url = urlparse(fix["patchUrl"])
            base_url = parsed_url[1]

            # add base url to version control platforms
            version_control_platforms.add(base_url)

            # ignore fixes from codeaurora -> site is archived
            if "codeaurora" in base_url:
                removed_commits += 1
                continue

            # fill in empty commit ids from all other sources
            if not fix["commitId"]:
                # find the commit id in the URL
                commitId = re.findall(regex, fix["patchUrl"])
                # ignore fixes with no commit id
                if len(commitId) == 0:
                    removed_commits += 1
                    continue
                fix["commitId"] = commitId

            commit_data[file_name].append(fix)
            vc_vulnerability_count[base_url] += 1

            # collect all gerrit based commits
            if "android.googlesource.com" in base_url:
                gerrit_commits.append((fix["patchUrl"], fix["commitId"]))
        
        # if no available commit data at all, skip this row completely
        if len(commit_data[file_name]) == 0:
            removed_rows += 1
            continue

        row = {
            "cveId" : entry["cveId"],
            "dateReported" : entry["dateReported"],
            "vulnerabilityType" : entry["vulnerabilityType"],
            "language" : entry["language"],
            "fixes" : commit_data[file_name],
            "severity" : entry["severity"],
            "component" : entry["component"]
        }
        writer.writerow(row)

print(vc_vulnerability_count.items())
counter = sorted(vc_vulnerability_count, key=lambda x: x[1])
print(counter)

print(f"removed_commits: {removed_commits}")
print(f"removed_rows: {removed_rows}")
print(f"{len(version_control_platforms)} # of version control platforms, version control = {version_control_platforms}")
print(f"CSV file has been created: {os.path.abspath(csv_file_path)}")


# scrape all commits from gerrit
csv_folder_path = "commits"
for url, commitId in gerrit_commits:
    try:
        res = requests.get(f"{url}?format=JSON")
        if not res.ok:
            continue
        with open(f"{csv_folder_path}/{commitId}.json", "wb") as f:
            f.write(res.content)
    except Exception as e:
        print(e)