# A9: Introduction and Motivations of Research

## rnn-commit-analysis

This folder contains some of the commit data gathered from malicious supply chain attacks, as well as the Python notebook used to analyze the data.

## agentic-data-generation

This folder contains the Python framework used to generate the data using the agents. The program can be run by adding `OPENAI_API_KEY` to the environment variable and running `python3 sim.py`. Various parameters such as the prompts and numbers of agents can be changed in `sim.py`, and the data will be saved to the folder `logs`.

In the `logs_example` folder there is a small example of the generated data where the malicious agents successfully gained maintainer status.

## aosp

```
Note: most of the data files have been removed for size constraints. The data can be found in the original dataset.
```

This source code utilizes the cves provided from the Github directory
https://github.com/quarkslab/aosp_dataset

The license provided is the original license that came with the dataset.
We've removed unrelated source files, as we only needed the cves to aggregate into a single csv dataset.

### Script

To invoke the script to convert all json files into a single csv, run:

`python3 convert_json_to_csv.py`

### Files

The files under `commits/` are the scraped commit metadata from Gerrit

The files under `cves/` are the original dataset files from the Github URL above.

The `output.csv` file is the new aggregated dataset.

The `convert_json_to_csv.py` is our script used to scrape/aggregate the data.
