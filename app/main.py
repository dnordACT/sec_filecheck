from pathlib import Path
from src.firebase_mgr import FirestoreManager
from src.sec_api_client import SecApiClient
import datetime

BASE_DIR = Path(__file__).resolve().parent

def main():
    # Initialize the database manager with the paths to the credentials
    database_mgr = FirestoreManager('website-sec-firebase-adminsdk-kv7ni-71e9c7b3db.json', 'website-sec')

    # Get the number of days since the last filing
    most_recent_filing = database_mgr.get_most_recent_date()
    today = datetime.date.today()
    days_since_last_filing = (today - most_recent_filing).days

    # Retrieve the list of companies from the companies table
    companies_info = database_mgr.get_all_companies()

    # Loop through each company and fetch the SEC filings
    for company in companies_info:
        company_id = company['id']
        name = company['company_name']
        cik_code = company['company_cik']

        print(f"Processing {name} with CIK: {cik_code}")

        # Initialize SEC API client for the company
        sec_client = SecApiClient()
        filings = sec_client.fetch_sec_filings(cik=cik_code, end_days=days_since_last_filing)
        if filings:
            for filing in filings:
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
                    database_mgr.add_filing(filing_data=filing_data)
                    print(f"Saved {name} {form} {link}")
        else:
            print(f"No new filings found for {name}")

    # Print success message
    print(f"Ran successfully: {datetime.datetime.now()}")

if __name__ == "__main__":
    main()
