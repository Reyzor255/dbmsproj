from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM departments")
        result = cursor.fetchone()
        conn.close()
        return f"Database connected! Found {result['count']} departments"
    else:
        return "Database connection failed!"

@app.route('/patients')
def patients():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY patient_name")
    patients = cursor.fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)

@app.route('/api/patients', methods=['GET', 'POST'])
def api_patients():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Received data: {data}")  # Debug print
            
            cursor.execute("""
                INSERT INTO patients (patient_name, age, gender, phone, address) 
                VALUES (%s, %s, %s, %s, %s)
            """, (data['patient_name'], data['age'], data['gender'], 
                  data['phone'], data['address']))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            print(f"Error adding patient: {e}")  # Debug print
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    cursor.execute("SELECT * FROM patients ORDER BY patient_name")
    patients = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in patients])

@app.route('/tokens')
def tokens():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor(dictionary=True)
    
    # Get tokens with JOIN query
    cursor.execute("""
        SELECT qt.*, p.patient_name, d.doctor_name, dept.dept_name
        FROM queue_tokens qt
        JOIN patients p ON qt.patient_id = p.patient_id
        JOIN doctors d ON qt.doctor_id = d.doctor_id
        JOIN departments dept ON qt.dept_id = dept.dept_id
        ORDER BY qt.appointment_time
    """)
    tokens = cursor.fetchall()
    
    cursor.execute("SELECT * FROM patients ORDER BY patient_name")
    patients = cursor.fetchall()
    
    cursor.execute("SELECT * FROM doctors ORDER BY doctor_name")
    doctors = cursor.fetchall()
    
    cursor.execute("SELECT * FROM departments ORDER BY dept_name")
    departments = cursor.fetchall()
    
    conn.close()
    return render_template('tokens.html', tokens=tokens, patients=patients, 
                         doctors=doctors, departments=departments)

@app.route('/api/tokens', methods=['GET', 'POST'])
def api_tokens():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Received token data: {data}")  # Debug print
            
            # Validate required fields
            required_fields = ['patient_id', 'doctor_id', 'dept_id', 'appointment_time']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            # Generate simple token number
            cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
            total_tokens = cursor.fetchone()['count']
            token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{(total_tokens + 1):04d}"
            
            print(f"Generated token number: {token_number}")  # Debug print
            
            # Insert token
            cursor.execute("""
                INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
                VALUES (%s, %s, %s, %s, %s, 'Waiting')
            """, (token_number, data['patient_id'], data['doctor_id'], data['dept_id'], 
                  data['appointment_time']))
            
            conn.commit()
            print(f"Token inserted successfully with ID: {cursor.lastrowid}")  # Debug print
            
            conn.close()
            return jsonify({'success': True, 'token_number': token_number})
            
        except mysql.connector.Error as db_error:
            print(f"Database error: {db_error}")  # Debug print
            conn.rollback()
            conn.close()
            return jsonify({'success': False, 'error': f'Database error: {str(db_error)}'}), 500
        except Exception as e:
            print(f"General error adding token: {e}")  # Debug print
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET request - return all tokens
    try:
        cursor.execute("""
            SELECT qt.*, p.patient_name, d.doctor_name, dept.dept_name
            FROM queue_tokens qt
            JOIN patients p ON qt.patient_id = p.patient_id
            JOIN doctors d ON qt.doctor_id = d.doctor_id
            JOIN departments dept ON qt.dept_id = dept.dept_id
            ORDER BY qt.appointment_time
        """)
        tokens = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in tokens])
    except Exception as e:
        print(f"Error fetching tokens: {e}")
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test-token')
def test_token():
    return render_template('test_token.html')

@app.route('/test-patient')
def test_patient():
    return render_template('test_patient.html')

if __name__ == '__main__':
    print("Starting Flask app...")
    print("Visit http://localhost:5000/test to check database connection")
    app.run(debug=True, port=5000)