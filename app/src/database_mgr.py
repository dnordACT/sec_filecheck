from datetime import datetime
import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        """Ensure the database and the required table exist, now including a 'link' column."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            company_name TEXT NOT NULL,
            source TEXT NOT NULL,
            link TEXT NOT NULL,
            summary TEXT
        );
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()

    def update_summary(self, company_name, source, link, summary=None):
        """Insert a new summary into the database, now including the 'link'."""
        today = datetime.now().date().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO summaries (date, company_name, source, link, summary) 
                           VALUES (?, ?, ?, ?, ?)""", (today, company_name, source, link, summary))
            conn.commit()
