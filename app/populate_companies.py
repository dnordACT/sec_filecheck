## This takes the company details from the company_list.csv file and populates the companies table in Firestore with the company details.

from pathlib import Path
from src.firebase_mgr import FirestoreManager
from src.sec_api_client import SecApiClient
import datetime
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

def main():
    # Initialize the database manager with the paths to the credentials
    database_mgr = FirestoreManager(BASE_DIR / 'website-sec-firebase-adminsdk-kv7ni-71e9c7b3db.json', 'website-sec')

    companies_info = pd.read_csv(BASE_DIR / 'data' / 'company_list.csv')
    companies_info['company_cik'] = companies_info['company_cik'].astype(str).str.zfill(10)
    company_id = companies_info['company_id']
    company_name = companies_info['company_name']
    company_cik = companies_info['company_cik']
    company_ticker = companies_info['company_ticker']
    assigned_to = companies_info['assigned_to']

    for i in range(len(company_id)):
        company_data = {
            'company_name': company_name[i],
            'company_cik': company_cik[i],
            'company_ticker': company_ticker[i],
            'assigned_to': assigned_to[i]
        }
    
        database_mgr.add_company(company_id[i], company_data)
        print(f"Added company {company_name[i]}")

if __name__ == "__main__":
    main()