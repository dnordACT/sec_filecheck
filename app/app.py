from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database/summaries.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM summaries")
    summaries = cur.fetchall()
    conn.close()
    return render_template('index.html', summaries=summaries)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
