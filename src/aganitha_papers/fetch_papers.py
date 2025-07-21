import requests
import xml.etree.ElementTree as ET
import csv
from typing import List, Tuple, Optional


def is_non_academic(affiliation: str) -> bool:
    company_keywords = [
        "inc", "ltd", "llc", "gmbh", "sas", "pvt", "company", "corporation", "corp",
        "biotech", "pharma", "pharmaceutical", "therapeutics", "genomics",
        "diagnostics", "research labs", "technologies", "solutions"
    ]
    affil_lower = affiliation.lower()
    return any(word in affil_lower for word in company_keywords)


def fetch_pubmed_ids(query: str) -> List[str]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": "100"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_pubmed_details(pubmed_id: str) -> Optional[Tuple[str, str, str, str, str, str]]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": pubmed_id, "retmode": "xml"}
    response = requests.get(url, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.text)

    title = ""
    pub_date = ""
    non_academic_authors = set()
    company_affiliations = set()
    corresponding_email = ""

    article = root.find(".//ArticleTitle")
    if article is not None:
        title = article.text or ""

    pub_date_node = root.find(".//PubDate/Year")
    if pub_date_node is not None:
        pub_date = pub_date_node.text or "Unknown"
    else:
        medline_date_node = root.find(".//PubDate/MedlineDate")
        if medline_date_node is not None:
            pub_date = medline_date_node.text or "Unknown"
        else:
            pub_date = "Unknown"

    for author in root.findall(".//Author"):
        affiliation_info = author.find("AffiliationInfo")
        if affiliation_info is not None:
            affiliation = affiliation_info.findtext("Affiliation", default="").strip()
            if is_non_academic(affiliation):
                last_name = author.findtext("LastName", default="")
                fore_name = author.findtext("ForeName", default="")
                full_name = f"{fore_name} {last_name}".strip()
                if full_name:
                    non_academic_authors.add(full_name)
                company_affiliations.add(affiliation)
            if "@" in affiliation and not corresponding_email:
                corresponding_email = affiliation.split()[-1].strip(".,;()")

    if non_academic_authors:
        return (
            pubmed_id,
            title,
            pub_date,
            "; ".join(non_academic_authors),
            "; ".join(company_affiliations),
            corresponding_email,
        )
    return None


def save_to_csv(filename: str, papers: List[Tuple[str, str, str, str, str, str]]) -> None:
    headers = [
        "PubmedID",
        "Title",
        "Publication Date",
        "Non-academic Author(s)",
        "Company Affiliation(s)",
        "Corresponding Author Email",
    ]
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(papers)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Search query for PubMed")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-f", "--filename", default="output_papers.csv", help="Output CSV filename")

    args = parser.parse_args()

    ids = fetch_pubmed_ids(args.query)
    papers = []
    for pid in ids:
        result = fetch_pubmed_details(pid)
        if result:
            papers.append(result)
            if args.debug:
                print(f"[+] Found: {result[1][:60]}...")

    save_to_csv(args.filename, papers)
    print(f"\nSaved {len(papers)} papers to {args.filename}")
    
    import pandas as pd
    df = pd.read_csv(args.filename, encoding='utf-8')
    print("\nCSV Preview:")
    print(df.head())
