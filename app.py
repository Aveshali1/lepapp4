from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Dotenv only local
if os.getenv("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)
CORS(app)

server = os.getenv('AZURE_SQL_SERVER')
database = os.getenv('AZURE_SQL_DATABASE')
username = os.getenv('AZURE_SQL_USERNAME')
password = os.getenv('AZURE_SQL_PASSWORD')

def get_connection():
    return __import__('pymssql').connect(
        server=server,
        user=username,
        password=password,
        database=database
    )

@app.route('/')
def index():
    return "Azure SQL API working"

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    u, p, pwd = data.get('username'), data.get('phone'), data.get('password')
    try:
        conn = get_connection()
        cur = conn.cursor(as_dict=True)
        cur.execute("SELECT Role FROM Users WHERE UserName=%s AND PhoneNo=%s AND Password=%s", (u,p,pwd))
        row = cur.fetchone()
        return jsonify({"status": "success", "role": row['Role']}) if row else (jsonify({"status": "failure"}), 401)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO PatientRawSubmission
            (UID, Name, DOB, Gender, PhoneNo, City, District, Lesion, Redness, Disability, NoSensation, NoneSymptoms, DirectContact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(data.get(k) for k in [
            'UID','Name','DOB','Gender','PhoneNo','City','District',
            'Lesion','Redness','Disability','NoSensation','NoneSymptoms','DirectContact'
        ]))
        conn.commit()
        return jsonify({"status": "success", "message": "Data submitted"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT",5000)))
