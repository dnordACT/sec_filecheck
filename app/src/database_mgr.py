from datetime import datetime
import sqlite3
import pandas as pd
from src.sec_api_client import SecApiClient

class DatabaseManager:
    def __init__(self, db_path, companies_csv_path):
        self.db_path = db_path
        self.companies_csv_path = companies_csv_path
        self.initialize_database()

    def initialize_database(self):
        """Ensure the database and the required tables exist, including summaries and companies."""
        create_summaries_table_query = """
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            company_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            form TEXT NOT NULL,
            link TEXT NOT NULL,
            summary TEXT,
            assigned_to TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (company_id)
        );
        """
        create_companies_table_query = """
        CREATE TABLE IF NOT EXISTS companies (
            company_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            company_ticker TEXT,
            company_cik TEXT,
            assigned_to TEXT,
            most_recent_date TEXT,
            most_recent_form TEXT,
            most_recent_link TEXT,
            most_recent_summary TEXT
        );
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(create_companies_table_query)
            cursor.execute(create_summaries_table_query)
            conn.commit()

        # if the companies table is empty, import data from the CSV file    
        if not self.is_companies_table_initialized():
            self.import_companies_data()

        if not self.is_summaries_table_initialized():
            self.populate_summaries_data()

    def is_companies_table_initialized(self):
        """Check if the companies table already contains data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM companies")
            count = cursor.fetchone()[0]
            return count > 0
        
    def is_summaries_table_initialized(self):
        """Check if the summaries table already contains data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM summaries")
            count = cursor.fetchone()[0]
            return count > 0
        
    def import_companies_data(self):
        """Import data from the provided CSV file into the companies table."""
        # Read CSV data
        dtype = {
            'company_id': str,
            'company_name': str,
            'company_ticker': str,
            'company_cik': str,
            'assigned_to': str
        }
        df = pd.read_csv(self.companies_csv_path, dtype=dtype)

        # Ensure the correct columns are present
        expected_columns = ['company_id', 'company_name', 'company_ticker', 'company_cik', 'assigned_to']
        if not all(col in df.columns for col in expected_columns):
            raise ValueError(f"CSV file is missing one or more of the required columns: {expected_columns}")

        # Insert the data into the companies table
        with sqlite3.connect(self.db_path) as conn:
            df[['company_id', 'company_name', 'company_ticker', 'company_cik', 'assigned_to']].to_sql('companies', conn, if_exists='append', index=False)

    def populate_summaries_data(self):
        """Fetch SEC filings for the past 365 days and populate the summaries table."""
        companies_info = self.get_company_info()

        for company in companies_info:
            company_id = company['company_id']
            name = company['company_name']
            cik_code = company['company_cik']

            print(f"Fetching filings for {name} (CIK: {cik_code})...")

            sec_client = SecApiClient(cik=cik_code)
            filings = sec_client.fetch_sec_filings(start_days=1, end_days=365)

            if filings:
                for filing in filings:
                    date = filing['recentFilingDate']
                    link = filing['link']
                    form = filing['form']
                    summary = filing.get('summary', None)

                    self.update_summary(date, company_id, name, form, link, summary)

                print(f"Fetched {len(filings)} filings for {name}.")
            else:
                print(f"No new filings found for {name}.")

    def get_company_info(self):
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("SELECT company_id, company_name, company_cik FROM companies", conn)
        return df.to_dict(orient='records')
    
    def update_summaries_assigned_to(self, company_id):
        """Update the assigned_to column in the summaries table based on the company_id."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE summaries
                SET assigned_to = (
                    SELECT assigned_to
                    FROM companies
                    WHERE company_id = ?
                )
                WHERE company_id = ?
            """, (company_id, company_id))
            conn.commit()

    def update_summary(self, date, company_id, company_name, form, link, summary=None):
        today = datetime.now().date().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO summaries (date, company_id, company_name, form, link, summary)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (date, company_id, company_name, form, link, summary))
            conn.commit()
            self.update_companies_table(company_id)
            self.update_summaries_assigned_to(company_id)

    def update_companies_table(self, company_id):
        """Update the companies table with the most recent form and summary for a given company."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            # Update the most recent source and summary for the company
            cur.execute("""
                UPDATE companies
                SET most_recent_date = (
                        SELECT s.date
                        FROM summaries s
                        WHERE s.company_id = companies.company_id
                        ORDER BY s.date DESC
                        LIMIT 1
                    ),
                    most_recent_form = (
                        SELECT s.form
                        FROM summaries s
                        WHERE s.company_id = companies.company_id
                        ORDER BY s.date DESC
                        LIMIT 1
                    ),
                    most_recent_link = (
                        SELECT s.link
                        FROM summaries s
                        WHERE s.company_id = companies.company_id
                        ORDER BY s.date DESC
                        LIMIT 1
                    ),
                    most_recent_summary = (
                        SELECT s.summary
                        FROM summaries s
                        WHERE s.company_id = companies.company_id
                        ORDER BY s.date DESC
                        LIMIT 1
                    )
                WHERE company_id = ?
            """, (company_id,))
            conn.commit()
