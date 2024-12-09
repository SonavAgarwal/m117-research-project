# Source
This source code utilizes the cves provided from the Github directory
https://github.com/quarkslab/aosp_dataset

The license provided is the original license that came with the dataset.
We've removed unrelated source files, as we only needed the cves to aggregate into a single csv dataset.

# Script

To invoke the script to convert all json files into a single csv, run:

`python3 convert_json_to_csv.py`

# Files

The files under `commits/` are the scraped commit metadata from Gerrit

The files under `cves/` are the original dataset files from the Github URL above.

The `output.csv` file is the new aggregated dataset.

The `convert_json_to_csv.py` is our script used to scrape/aggregate the data.

And the `LICENSE` is the origina license from the dataset https://github.com/quarkslab/aosp_dataset
