from src.firebase_mgr import FirestoreManager
import datetime

def main():
    # Initialize the database manager with the paths to the credentials
    database_mgr = FirestoreManager('website-sec-firebase-adminsdk-kv7ni-71e9c7b3db.json', 'website-sec')

    most_recent_filing = database_mgr.get_most_recent_date()
    today = datetime.date.today()
    days_since_last_filing = (today - most_recent_filing).days
    print(days_since_last_filing)

if __name__ == "__main__":
    main()