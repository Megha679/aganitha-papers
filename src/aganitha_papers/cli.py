import argparse
from aganitha_papers.fetch import fetch_papers, save_to_csv, print_debug

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers based on a query.")
    parser.add_argument("query", type=str, help="PubMed search query (in quotes)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-f", "--file", type=str, help="Filename to save results as CSV")

    args = parser.parse_args()

    try:
        papers = fetch_papers(args.query, debug=args.debug)

        if not papers:
            print("No matching papers with non-academic authors found.")
            return

        if args.file:
            save_to_csv(args.file, papers)
            print(f"✅ Saved {len(papers)} papers to {args.file}")
        else:
            for paper in papers:
                print_debug(paper)

    except Exception as e:
        print(f"❌ Error: {e}")

