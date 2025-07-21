&nbsp;Aganitha Papers



A command-line tool to fetch research papers from PubMed based on a query, filter them for pharmaceutical/biotech company-affiliated authors, and save the results as a CSV file.



---



&nbsp;Features



&nbsp;Fetches research papers from \*\*PubMed\*\* using its API.

\-  Identifies \*\*non-academic authors\*\* affiliated with \*\*pharma or biotech companies\*\*.

\-  Saves results to a \*\*CSV\*\* with the following columns:

&nbsp; - PubmedID

&nbsp; - Title

&nbsp; - Publication Date

&nbsp; - Non-academic Author(s)

&nbsp; - Company Affiliation(s)

&nbsp; - Corresponding Author Email

\-  Command-line support with helpful flags.

\-  Packaged with \*\*Poetry\*\* for clean dependency management and distribution.



---



&nbsp;Project Structure



aganitha-papers/

├── src/

│ └── aganitha\_papers/

│ ├── init.py

│ ├── fetch.py # Core logic (API calls, parsing, filtering)

│ └── cli.py # Command-line interface

├── tests/ # (Optional) Unit tests

├── pyproject.toml # Poetry config

├── README.md



---



&nbsp;Installation



1\. \*\*Clone the repo\*\*:

&nbsp;  ```bash

&nbsp;  git clone https://github.com/<your-username>/aganitha-papers.git

&nbsp;  cd aganitha-papers

2\. Install Poetry dependencies:



bash

poetry install

Usage

Run the CLI with a PubMed search query:

poetry run get-papers-list "cancer AND immunotherapy" -f results.csv

| Option        | Description                            |

| ------------- | -------------------------------------- |

| `-h, --help`  | Show usage instructions                |

| `-d, --debug` | Enable debug logging                   |

| `-f FILE`     | Save results to specified CSV filename |

&nbsp;Heuristics for Non-Academic Authors

To identify non-academic authors, we apply rules like:



Email domains (e.g., @pfizer.com, @novartis.com)



Affiliations lacking academic keywords (e.g., not containing "university", "institute", "college", "school", "hospital")



Presence of pharma/biotech keywords

Example

poetry run get-papers-list "diabetes treatment" -f diabetes.csv

Output:

Saved 8 papers to diabetes.csv

Publishing (Test PyPI)

To publish to Test PyPI:

poetry config repositories.testpypi https://test.pypi.org/legacy/

poetry publish --build --repository testpypi

Tools \& Libraries Used

requests – HTTP requests to PubMed API



pandas – CSV creation and data handling



lxml – Parsing XML from PubMed



Poetry – Packaging and dependency management

&nbsp;Evaluation Criteria Checklist

&nbsp;Modular code structure (fetch.py, cli.py)



&nbsp;Command-line interface using argparse



&nbsp;CSV output format



&nbsp;Poetry-based install + executable command



&nbsp;Typed functions and docstrings



&nbsp;Error handling for API/data issues



&nbsp;README with instructions and tool references









