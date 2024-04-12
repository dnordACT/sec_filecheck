from sec_api_client import SecApiClient
from file_manager import FileManager
from database_mgr import DatabaseManager
from pathlib import Path
import os
import json
import datetime

# Load the JSON of companies as a dictionary.
with open("company_codes.json") as file:
    company_codes = json.load(file)

def main():
    companies_info = company_codes

    database_mgr = DatabaseManager("summaries.db")

    # Loops through the list from company_codes.  Now all we need to do is update tthe company_codes.json to add or remove companies.
    for cik, name in companies_info.items():
        print(f"Processing {name} with CIK: {cik}")

        # Initialize SEC API client for the company
        sec_client = SecApiClient(cik=cik)
        filings = sec_client.fetch_sec_filings()

        if filings:
            # Initialize File Manager to save filings
            file_manager = FileManager(cik=cik, company_name=name, filings=filings)
            saved_files = file_manager.save_filings()

            for filing in saved_files:
                file_path = filing['file_path']  # Assuming save_filings now returns a dict with file_path and link
                link = filing['link']  # Get the link from the filing information

                source_name = Path(file_path).stem

                # Update the database with the new link parameter
                database_mgr.update_summary(name, source_name, link)

        else:
            print(f"No new filings found for {name}")

    # Print success message
    print(f"Ran successfully on {datetime.date.today()}")

if __name__ == "__main__":
    main()
