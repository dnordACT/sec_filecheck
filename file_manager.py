import os
import requests
from datetime import datetime, timedelta


class FileManager:
    def __init__(self, cik, company_name, filings, base_folder="filings"):
        self.cik = cik
        self.company_name = company_name
        self.filings = filings
        self.base_folder = base_folder
    
    def save_filings(self):
        saved_files = []
        current_date = datetime.now()
        week_ago = current_date - timedelta(days=7)
        for filing in self.filings:
            accession_number = filing['accessionNumber']
            primary_document = filing['primaryDocument']
            url = f"https://sec.gov/Archives/edgar/data/{self.cik}/{accession_number}/{primary_document}"
            response = requests.get(url, headers={"User-Agent": "CompanyName/YourName (YourEmail)"})
            if response.status_code == 200:
                file_name = self._generate_filename(filing)
                folder_path = os.path.join(self.base_folder, self.company_name, f"Week_of_{week_ago.strftime('%Y-%m-%d')}")
                os.makedirs(folder_path, exist_ok=True)
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"File saved: {file_path}")
                saved_files.append({'file_path': file_path, 'link': url})  # Modified to return a dict with file_path and link
            else:
                print(f"Failed to retrieve file: {response.status_code}, URL: {url}")
        return saved_files

    def _generate_filename(self, filing):
        accession_number = filing['accessionNumber']
        primary_document = filing['primaryDocument']
        file_name = f"{filing['recentFilingDate']}_{filing['form']}_{accession_number[-6:]}"
        file_extension = os.path.splitext(primary_document)[1]
        if file_extension == ".htm":
            file_extension = ".html"
        file_name += file_extension
        return file_name
