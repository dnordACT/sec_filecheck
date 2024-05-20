from src.sec_api_client import SecApiClient
from src.firebase_mgr import FirestoreManager
import pandas as pd

def main():
    # Initialize the database manager with the paths to the credentials
    database_manager = FirestoreManager('website-sec-firebase-adminsdk-kv7ni-71e9c7b3db.json', 'website-sec')

    companies = database_manager.get_all_companies()
    # Retrieve all companies from the database

    for company in companies:
        sec_client = SecApiClient()
        print(f"Company data: {company}")

        company_id = company['id']
        name = company['company_name']
        cik_code = company['company_cik']

        print(f"Processing {name} with CIK: {cik_code}")

        # Fetch SEC filings for the company
        sec_filings = sec_client.fetch_sec_filings(cik_code, start_days=2, end_days=365)

        if sec_filings:
            for filing in sec_filings:
                date = filing['recentFilingDate']
                link = filing['link']
                form = filing['form']

                filing_data = {
                    'company_id': company_id,
                    'company_name': name,
                    'form_date': date,
                    'form_link': link,
                    'form_type': form
                }

                # Add the filing to the database without specifying filing_id
                if form in ['10-K', '10-Q', '8-K', '10-K/A', '10-Q/A', '8-K/A', '6-K', '6-K/A', 'ARS', '20-F', '20-F/A', '40-F', '40-F/A']:
                    database_manager.add_filing(filing_data=filing_data)
                    print(f"Saved {name} {form} {link}")
        else:
            print(f"No new filings found for {name}")

if __name__ == "__main__":
    main()
