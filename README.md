# SEC Data Collector and Viewer

If running on apache server, make sure to run 0 12 * * * /usr/bin/python3 /var/www/sec_filecheck/app/main.py >> /var/log/mycronlog.log 2>&1 in crontab

This project collects company data from the SEC and provides a web interface for viewing the data.

## Project Structure

the 'app' folder contains all of the 

app/data/ # Directory for data files company_codes.json filings/ 
app/database/ # Directory for database files summaries.db 
app/src/ # Directory for source code files sec_api_client.py file_manager.py database_mgr.py
templates/ # Directory for Flask templates index.html 

main.py # Script to collect data 

app.py # Flask app 

requirements.txt # Python dependencies


## Functionality

- `main.py`: This script collects data from the SEC. It uses the `sec_api_client.py`, `file_manager.py`, and `database_mgr.py` files in the `src/` directory to fetch and process the data. The data is saved in the `data/` and `database/` directories.

- `app.py`: This is a Flask app that provides a web interface for viewing the data. It fetches data from the `database/summaries.db` database and generates HTML using the `templates/index.html` template.

## How to Run

1. Install the Python dependencies: `pip install -r requirements.txt`
2. Run the data collection script: `python main.py`
3. Start the Flask app: `python app.py`