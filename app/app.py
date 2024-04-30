from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'database', 'summaries.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM summaries ORDER BY date(date) DESC")
    summaries = cur.fetchall()
    conn.close()
    return render_template('index.html', summaries=summaries)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)