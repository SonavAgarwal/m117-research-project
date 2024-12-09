# A9: Introduction and Motivations of Research

## rnn-commit-analysis

This folder contains some of the commit data gathered from malicious supply chain attacks, as well as the Python notebook used to analyze the data.

In the notebook, the first section performs the logistic regression analysis on the data, and the second section performs the RNN analysis on the data.

The data in the `malicious` and `not-malicious` folders were gathered by cloning the repositories and using the `git log` command to gather the commit data. The data was then cleaned and saved, and the code to parse it is in the notebook.

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

## synthetic-data-with-gpt

This folder contains the Python notebook used to generate synthetic data using GPT, and the generated data in csv format.

## java-vulnerability-dataset

This folder contains the scripts used to find the commits associated with certain CVEs, as well as some of the data gathered.

The source of this dataset is provided from the Github repository:

https://github.com/tuhh-softsec/A-Manually-Curated-Dataset-of-Vulnerability-Introducing-Commits-in-Java/tree/main

## repository source:

https://github.com/tuhh-softsec/A-Manually-Curated-Dataset-of-Vulnerability-Introducing-Commits-in-Java/tree/main

### json source:

https://github.com/tuhh-softsec/A-Manually-Curated-Dataset-of-Vulnerability-Introducing-Commits-in-Java/blob/main/dataset/tool_assisted_manual_dataset.json

### csv with names:

https://github.com/tuhh-softsec/A-Manually-Curated-Dataset-of-Vulnerability-Introducing-Commits-in-Java/blob/main/review_pipeline/cve_to_cwe.csv

### Script

To invoke the scrip that converts the json into a single csv dataset, run:

`python3 convert_json_to_csv.py`

Also, in order to scrape commit data from Github, you must have a Github access token. Then, fill in your access token as indicated by the comments and run:

`python3 scrape_github.py`
