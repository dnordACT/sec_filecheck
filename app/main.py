from src.sec_api_client import SecApiClient
from src.file_manager import FileManager
from src.database_mgr import DatabaseManager
from pathlib import Path
import os
import json
import datetime

BASE_DIR = Path(__file__).resolve().parent

# Load the JSON of companies as a dictionary.
with open(BASE_DIR / "data" / "company_codes.json") as file:
    company_codes = json.load(file)

def main():
    companies_info = company_codes

    database_mgr = DatabaseManager(str(BASE_DIR / "database" / "summaries.db"))

    # Loops through the list from company_codes.  Now all we need to do is update tthe company_codes.json to add or remove companies.
    for cik, name in companies_info.items():
        print(f"Processing {name} with CIK: {cik}")

        # Initialize SEC API client for the company
        sec_client = SecApiClient(cik=cik)
        filings = sec_client.fetch_sec_filings()
        if filings:

            for filing in filings:
                link = filing['link']
                form = filing['form']

                if form not in ['424B2', '424B5', 'FWP']:
                    database_mgr.update_summary(name, form, link)
                    print(f'saved {name} {form} {link}')

        # this part of the script is requried if I want to save the filings to a local directory and then upload to an AI model.
        # if filings:
        #     # Initialize File Manager to save filings
        #     file_manager = FileManager(cik=cik, company_name=name, filings=filings)
        #     saved_files = file_manager.save_filings()


        else:
            print(f"No new filings found for {name}")

    # Print success message
    print(f"Ran successfully on {datetime.date.today()}")

if __name__ == "__main__":
    main()


