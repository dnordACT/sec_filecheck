from flask import Flask, render_template, send_file
import sqlite3
import pandas as pd

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database/summaries.db')
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

@app.route('/export', methods=['GET'])
def export():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM summaries", conn)
    df.to_csv('database/summaries.csv', index=False)
    conn.close()
    return send_file('database/summaries.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
