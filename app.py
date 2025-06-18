from flask import Flask, request, jsonify
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Azure SQL DB connection config
server = os.getenv('AZURE_SQL_SERVER')
database = os.getenv('AZURE_SQL_DATABASE')
username = os.getenv('AZURE_SQL_USERNAME')
password = os.getenv('AZURE_SQL_PASSWORD')
driver = '{ODBC Driver 17 for SQL Server}'

# Function to connect to Azure SQL
def get_connection():
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    return pyodbc.connect(conn_str)

# Index route to check status
@app.route('/')
def index():
    return "Azure SQL API working"

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    phone = data.get('phone')
    password_input = data.get('password')

    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        SELECT Role FROM Users 
        WHERE UserName = ? AND PhoneNo = ? AND Password = ?
        """
        cursor.execute(query, (username, phone, password_input))
        row = cursor.fetchone()
        if row:
            return jsonify({"status": "success", "role": row.Role}), 200
        else:
            return jsonify({"status": "failure", "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Submit patient data endpoint
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

# Start the server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
