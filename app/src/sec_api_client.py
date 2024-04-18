import requests
from datetime import datetime, timedelta

class SecApiClient:
    def __init__(self, cik, user_agent="CompanyName/YourName (YourEmail)"):
        self.cik = cik
        self.base_url = "https://data.sec.gov/submissions/CIK{}.json"
        self.document_base_url = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_slash}/{primary_document}"
        self.user_agent = user_agent
        self.filings = []
    
    def fetch_sec_filings(self):
        # Checks for todays date and the date a day ago.  This is to determine which filings happened in the past day.
        current_date = datetime.now()
        day_ago = current_date - timedelta(days=1)
        url = self.base_url.format(self.cik)
        
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            recent_filings = data.get('filings', {}).get('recent', {})
            for date, accession_number, form, primary_document in zip(recent_filings.get('filingDate', []),
                                                                       recent_filings.get('accessionNumber', []),
                                                                       recent_filings.get('form', []),
                                                                       recent_filings.get('primaryDocument', [])):
                if datetime.strptime(date, '%Y-%m-%d') > day_ago:
                    accession_no_slash = accession_number.replace('-', '')
                    document_url = self.document_base_url.format(cik=self.cik, accession_no_slash=accession_no_slash, primary_document=primary_document)
                    self.filings.append({
                        "recentFilingDate": date,
                        "accessionNumber": accession_no_slash,
                        "form": form,
                        "primaryDocument": primary_document,
                        "link": document_url  # Add the full URL for the filing
                    })
        else:
            print(f"Failed to fetch data for CIK {self.cik}: HTTP {response.status_code}")
        return self.filings
