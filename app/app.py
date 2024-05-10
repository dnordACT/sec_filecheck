from flask import Flask, render_template, request
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
    company_name = request.args.get('company_name', '')
    assigned_to = request.args.get('assigned_to', '')
    form = request.args.get('form', '')

    query = "SELECT * FROM summaries WHERE 1=1"
    filters = []

    if company_name:
        query += " AND company_name = ?"
        filters.append(company_name)

    if assigned_to:
        query += " AND assigned_to = ?"
        filters.append(assigned_to)

    if form:
        query += " AND form = ?"
        filters.append(form)

    query += " ORDER BY date(date) DESC"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, filters)
    summaries = cur.fetchall()

    # Fetch available filter options
    cur.execute("SELECT DISTINCT company_name FROM summaries ORDER BY company_name")
    company_names = cur.fetchall()

    cur.execute("SELECT DISTINCT assigned_to FROM summaries ORDER BY assigned_to")
    assigned_tos = cur.fetchall()

    cur.execute("SELECT DISTINCT form FROM summaries ORDER BY form")
    forms = cur.fetchall()

    conn.close()
    return render_template('index.html', summaries=summaries, company_names=company_names, assigned_tos=assigned_tos, forms=forms)

@app.route('/companies')
def companies():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT company_name FROM companies ORDER BY company_name")
    company_names = cur.fetchall()
    selected_company = request.args.get('company_name', '')

    if selected_company:
        cur.execute("""
            SELECT * FROM companies WHERE company_name = ?
        """, (selected_company,))
        company_info = cur.fetchone()
    else:
        company_info = None

    conn.close()
    return render_template('companies.html', company_info=company_info, company_names=company_names)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)