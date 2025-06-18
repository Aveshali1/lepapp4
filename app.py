from flask import Flask, request, jsonify
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()  # Load env variables

app = Flask(__name__)

# DB config
server = os.getenv('AZURE_SQL_SERVER')
database = os.getenv('AZURE_SQL_DATABASE')
username = os.getenv('AZURE_SQL_USERNAME')
password = os.getenv('AZURE_SQL_PASSWORD')
driver = '{ODBC Driver 17 for SQL Server}'

# Connection function
def get_connection():
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    return pyodbc.connect(conn_str)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    phone = data.get('phone')
    password = data.get('password')

    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        SELECT * FROM Users 
        WHERE UserName = ? AND PhoneNo = ? AND Password = ?
        """
        cursor.execute(query, (username, phone, password))
        row = cursor.fetchone()
        if row:
            return jsonify({"status": "success", "role": row.Role}), 200
        else:
            return jsonify({"status": "failure", "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO PatientRawSubmission
        (UID, Name, DOB, Gender, PhoneNo, City, District, Lesion, Redness, Disability, NoSensation, NoneSymptoms, DirectContact)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            data.get('UID'),
            data.get('Name'),
            data.get('DOB'),
            data.get('Gender'),
            data.get('PhoneNo'),
            data.get('City'),
            data.get('District'),
            data.get('Lesion'),
            data.get('Redness'),
            data.get('Disability'),
            data.get('NoSensation'),
            data.get('NoneSymptoms'),
            data.get('DirectContact')
        ))
        conn.commit()
        return jsonify({"status": "success", "message": "Data submitted"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "Azure SQL API working"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
