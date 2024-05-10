from pathlib import Path
from src.database_mgr import DatabaseManager
from src.sec_api_client import SecApiClient
import datetime

BASE_DIR = Path(__file__).resolve().parent

def main():
    # Initialize the database manager with the paths to the SQLite database and CSV file
    database_mgr = DatabaseManager(str(BASE_DIR / "database" / "summaries.db"), str(BASE_DIR / "data" / "company_list.csv"))

    # Retrieve the list of companies from the companies table
    companies_info = database_mgr.get_company_info()

    for company in companies_info:
        company_id = company['company_id']  # Ensure this is not a tuple
        name = company['company_name']
        cik_code = company['company_cik']

        print(f"Processing {name} with CIK: {cik_code}")

        # Initialize SEC API client for the company (dummy class here, replace with the actual one)
        sec_client = SecApiClient(cik=cik_code)
        filings = sec_client.fetch_sec_filings()
        if filings:
            for filing in filings:
                date = filing['recentFilingDate']
                link = filing['link']
                form = filing['form']

                database_mgr.update_summary(date, company_id, name, form, link)
                print(f'Saved {name} {form} {link}')

        else:
            print(f"No new filings found for {name}")

    # Print success message
    print(f"Ran successfully on {datetime.date.today()}")

if __name__ == "__main__":
    main()
