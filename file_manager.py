import os
import requests
from datetime import datetime, timedelta
import re


class FileManager:
    def __init__(self, cik, company_name, filings, base_folder="filings"):
        self.cik = cik
        self.company_name = company_name
        self.filings = filings
        self.base_folder = base_folder
    
    def save_filings(self):
        saved_files = []
        current_date = datetime.now()
        day_ago = current_date - timedelta(days=1)
        for filing in self.filings:
            accession_number = filing['accessionNumber']
            primary_document = filing['primaryDocument']
            url = f"https://sec.gov/Archives/edgar/data/{self.cik}/{accession_number}/{primary_document}"
            response = requests.get(url, headers={"User-Agent": "CompanyName/YourName (YourEmail)"})
            if response.status_code == 200:
                file_name = self._generate_filename(filing)
                folder_path = os.path.join(self.base_folder, self.company_name, f"Day_of_{day_ago.strftime('%Y-%m-%d')}")
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

class FileConverter:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def convert_to_text(self):
        # Read the file content
        with open(self.file_path, 'rb') as file:
            content = file.read().decode('utf-8')
        
        # Check if the file is HTML and remove tags if it is
        if os.path.splitext(self.file_path)[1].lower() == '.html':
            content = re.sub('<[^<]+?>', '', content)
        
        # Save the processed content to a .txt file
        new_file_path = os.path.splitext(self.file_path)[0] + '.txt'
        with open(new_file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(content)
        
        return new_file_path