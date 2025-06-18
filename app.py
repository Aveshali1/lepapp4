from flask import Flask, request, jsonify
import os
import pymssql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Read DB credentials
server = os.getenv('AZURE_SQL_SERVER')
database = os.getenv('AZURE_SQL_DATABASE')
username = os.getenv('AZURE_SQL_USERNAME')
password = os.getenv('AZURE_SQL_PASSWORD')

# DB connection
def get_connection():
    return pymssql.connect(server, username, password, database)

# Health check
@app.route('/')
def index():
    return "Azure SQL API working"

# Login API
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username_input = data.get('username')
    phone = data.get('phone')
    password_input = data.get('password')
    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute("""
            SELECT Role FROM Users 
            WHERE UserName = %s AND PhoneNo = %s AND Password = %s
        """, (username_input, phone, password_input))
        result = cursor.fetchone()
        conn.close()
        if result:
            return jsonify({"status": "success", "role": result["Role"]}), 200
        else:
            return jsonify({"status": "failure", "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Submit patient data
@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO PatientRawSubmission 
            (UID, Name, DOB, Gender, PhoneNo, City, District, Lesion, Redness, Disability, NoSensation, NoneSymptoms, DirectContact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('UID'), data.get('Name'), data.get('DOB'), data.get('Gender'),
            data.get('PhoneNo'), data.get('City'), data.get('District'),
            data.get('Lesion'), data.get('Redness'), data.get('Disability'),
            data.get('NoSensation'), data.get('NoneSymptoms'), data.get('DirectContact')
        ))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Data submitted"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start Flask
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
