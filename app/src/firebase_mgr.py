import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

class FirestoreManager:
    def __init__(self, service_account_path, project_id):
        # Initialize the Firebase Admin SDK
        self.cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(self.cred, {'projectId': project_id})
        # Initialize Firestore client
        self.db = firestore.client()
        print(f"Initialized Firestore with project: {project_id}")

    def add_company(self, company_id, company_data):
        """Adds a company document to the companies collection."""
        company_ref = self.db.collection('companies').document(company_id)
        company_ref.set(company_data)
        print(f"Company {company_id} added successfully.")

    def add_filing_test(self, filing_data, filing_id=None):
        """Adds a filing document to the filings collection."""
        if filing_id:
            filing_ref = self.db.collection('filingstest').document(filing_id)
            filing_ref.set(filing_data)
            print(f"Filing {filing_id} added successfully.")
        else:
            filing_ref = self.db.collection('filingstest').add(filing_data)
            print(f"Filing added with ID {filing_ref[1].id} successfully.")

    def add_filing(self, filing_data, filing_id=None):
        """Adds a filing document to the filings collection."""
        if filing_id:
            filing_ref = self.db.collection('filings').document(filing_id)
            filing_ref.set(filing_data)
            print(f"Filing {filing_id} added successfully.")
        else:
            filing_ref = self.db.collection('filings').add(filing_data)
            print(f"Filing added with ID {filing_ref[1].id} successfully.")

    def get_most_recent_date(self):
        """Retrieves the most recent filing date."""
        filings_ref = self.db.collection('filings').order_by('form_date', direction=firestore.Query.DESCENDING).limit(1)
        for doc in filings_ref.stream():
            data = doc.to_dict()
            date = datetime.strptime(data['form_date'], '%Y-%m-%d').date()
            return date

    def get_recent_filing_for_each_company(self):
        """Retrieves the most recent filing for each company."""
        filings_ref = self.db.collection('filings').order_by('form_date', direction=firestore.Query.DESCENDING)
        filings = {}
        for doc in filings_ref.stream():
            data = doc.to_dict()
            if data['company_id'] not in filings:
                filings[data['company_id']] = data
        return filings

    def get_filings_for_company(self, company_id):
        """Retrieves all filings for a specific company."""
        filings_ref = self.db.collection('filings').where('company_id', '==', company_id)
        filings = [doc.to_dict() for doc in filings_ref.stream()]
        return filings
    
    def get_all_companies(self):
        """Retrieves all documents from the companies collection."""
        companies_ref = self.db.collection('companies')
        companies = []
        for doc in companies_ref.stream():
            company = doc.to_dict()
            company['id'] = doc.id  # Include the document ID in the data
            companies.append(company)
        print(f"Retrieved {len(companies)} companies")
        return companies
    
