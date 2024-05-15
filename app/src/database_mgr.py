from datetime import datetime
import pandas as pd
from src.sec_api_client import SecApiClient
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, DDL, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import sqlalchemy
import os

class DatabaseManager:
    def __init__(self, companies_csv_path):
        load_dotenv()  # Load environment variables from .env file
        self.engine = self.connect_tcp_socket()
        self.companies_csv_path = companies_csv_path
        self.metadata = MetaData()
        self.initialize_database()
        self.check_and_import_companies_data()
        self.check_and_populate_summaries_data()

    def connect_tcp_socket(self) -> sqlalchemy.engine.base.Engine:
        db_host = os.getenv("INSTANCE_CONNECTION_NAME")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")
        db_port = os.getenv("DB_PORT")
        print(f"Host: {db_host}, Port: {db_port}, User: {db_user}, Database: {db_name}")
        engine = create_engine(
            sqlalchemy.engine.URL.create(
                drivername="postgresql+pg8000",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_name,
            ),
        )
        return engine

    def initialize_database(self):
        create_summaries_table_query = DDL("""
        CREATE TABLE IF NOT EXISTS summaries (
            id SERIAL PRIMARY KEY,
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
        )
        create_companies_table_query = DDL("""
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
        )
        try:
            with self.engine.begin() as connection:
                connection.execute(create_companies_table_query)
                connection.execute(create_summaries_table_query)

            # Additional logic as before
        except SQLAlchemyError as e:
            print(f"Error during initialization: {e}")

    def check_and_import_companies_data(self):
        """Check if the companies table is empty and import data if necessary."""
        if not self.is_companies_table_initialized():
            print("Companies table is empty. Importing data...")
            self.import_companies_data()

    def check_and_populate_summaries_data(self):
        """Check if the summaries table is empty and populate data if necessary."""
        if not self.is_summaries_table_initialized():
            print("Summaries table is empty. Populating data...")
            self.populate_summaries_data()

    def is_companies_table_initialized(self):
        """Check if the companies table already contains data."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT COUNT(*) FROM companies"))
                count = result.scalar()
                return count > 0
        except SQLAlchemyError as e:
            print(f"Error checking companies table: {e}")
        return False

    def is_summaries_table_initialized(self):
        """Check if the summaries table already contains data."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT COUNT(*) FROM summaries"))
                count = result.scalar()
                return count > 0
        except SQLAlchemyError as e:
            print(f"Error checking summaries table: {e}")
        return False

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
        try:
            with self.engine.begin() as connection:
                df[['company_id', 'company_name', 'company_ticker', 'company_cik', 'assigned_to']].to_sql('companies', connection, if_exists='append', index=False)
        except SQLAlchemyError as e:
            print(f"Error importing companies data: {e}")

    def populate_summaries_data(self):
        """Fetch SEC filings for the past 365 days and populate the summaries table."""
        companies_info = self.get_company_info()

        for company in companies_info:
            company_id = company['company_id']
            name = company['company_name']
            cik_code = company['company_cik']

            print(f"Fetching filings for {name} (CIK: {cik_code})...")

            sec_client = SecApiClient(cik=cik_code)
            filings = sec_client.fetch_sec_filings(start_days=2, end_days=365)

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
        try:
            with self.engine.connect() as connection:
                df = pd.read_sql_query(DDL("SELECT company_id, company_name, company_cik FROM companies"), connection)
            return df.to_dict(orient='records')
        except SQLAlchemyError as e:
            print(f"Error fetching company info: {e}")
        return []

    def update_summaries_assigned_to(self, company_id):
        """Update the assigned_to column in the summaries table based on the company_id."""
        update_query = text("""
            UPDATE summaries
            SET assigned_to = (
                SELECT assigned_to
                FROM companies
                WHERE company_id = :company_id
            )
            WHERE company_id = :company_id
        """
        )
        try:
            with self.engine.begin() as connection:
                connection.execute(update_query, {"company_id": company_id})
        except SQLAlchemyError as e:
            print(f"Error updating summaries assigned_to: {e}")

    def update_summary(self, date, company_id, company_name, form, link, summary=None):
        today = datetime.now().date().strftime("%Y-%m-%d")
        insert_query = text("""
            INSERT INTO summaries (date, company_id, company_name, form, link, summary)
            VALUES (:date, :company_id, :company_name, :form, :link, :summary)
        """
        )
        try:
            with self.engine.begin() as connection:
                connection.execute(insert_query, {
                    "date": date, 
                    "company_id": company_id,
                    "company_name": company_name,
                    "form": form,
                    "link": link,
                    "summary": summary
                })
            self.update_companies_table(company_id)
            self.update_summaries_assigned_to(company_id)
        except SQLAlchemyError as e:
            print(f"Error updating summary: {e}")

    def update_companies_table(self, company_id):
        """Update the companies table with the most recent form and summary for a given company."""
        update_query = text("""
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
            WHERE company_id = :company_id
        """
        )
        try:
            with self.engine.begin() as connection:
                connection.execute(update_query, {"company_id": company_id})
        except SQLAlchemyError as e:
            print(f"Error updating companies table: {e}")