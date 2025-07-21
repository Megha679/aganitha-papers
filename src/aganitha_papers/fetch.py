from typing import List, Dict
import requests
import xml.etree.ElementTree as ET
import csv

# Heuristic keywords to detect non-academic affiliation
NON_ACADEMIC_KEYWORDS = ["pharma", "biotech", "inc", "ltd", "llc", "gmbh", "pvt", "company", "corp", "corporation", "therapeutics", "laboratories", "biosciences"]

def fetch_papers(query: str, debug: bool = False) -> List[Dict[str, str]]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Step 1: Search for paper IDs
    search_url = f"{base_url}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": 30,
        "retmode": "json"
    }
    search_resp = requests.get(search_url, params=search_params)
    search_resp.raise_for_status()
    ids = search_resp.json()["esearchresult"]["idlist"]
    if debug:
        print(f"[DEBUG] Found {len(ids)} paper IDs")

    if not ids:
        return []

    # Step 2: Fetch paper summaries
    fetch_url = f"{base_url}efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml"
    }
    fetch_resp = requests.get(fetch_url, params=fetch_params)
    fetch_resp.raise_for_status()
    root = ET.fromstring(fetch_resp.content)

    papers = []

    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        pub_date_elem = article.find(".//PubDate")
        pub_date = extract_pub_date(pub_date_elem)

        non_academic_authors = []
        company_affiliations = []
        email = None

        for author in article.findall(".//Author"):
            affil = author.findtext(".//AffiliationInfo/Affiliation")
            if affil:
                affil_lower = affil.lower()
                if any(keyword in affil_lower for keyword in NON_ACADEMIC_KEYWORDS):
                    fullname = f"{author.findtext('ForeName', '')} {author.findtext('LastName', '')}".strip()
                    non_academic_authors.append(fullname)
                    company_affiliations.append(affil)
                    if not email:
                        email = extract_email(affil)

        if non_academic_authors:
            papers.append({
                "PubmedID": pmid,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academic Author(s)": "; ".join(non_academic_authors),
                "Company Affiliation(s)": "; ".join(company_affiliations),
                "Corresponding Author Email": email or ""
            })

    return papers

def extract_pub_date(pub_date_elem):
    if pub_date_elem is None:
        return "N/A"
    year = pub_date_elem.findtext("Year", "")
    month = pub_date_elem.findtext("Month", "")
    day = pub_date_elem.findtext("Day", "")
    return f"{year}-{month or '01'}-{day or '01'}"

def extract_email(affil: str) -> str:
    import re
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", affil)
    return match.group(0) if match else ""

def save_to_csv(filename: str, papers: List[Dict[str, str]]):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "PubmedID", "Title", "Publication Date",
            "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"
        ])
        writer.writeheader()
        writer.writerows(papers)

def print_debug(paper: Dict[str, str]):
    print("\n--- Paper ---")
    for key, value in paper.items():
        print(f"{key}: {value}")
