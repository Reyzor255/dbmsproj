from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'hospital_secret_key_2024'

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role check decorator
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                return jsonify({'success': False, 'error': 'Access denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',  # Your MySQL password
    'database': 'hospital_queue_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Login routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                      (data['username'], data['password']))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Home page
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Departments CRUD
@app.route('/departments')
@login_required
def departments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departments ORDER BY dept_id")
    departments = cursor.fetchall()
    conn.close()
    return render_template('departments.html', departments=departments)

@app.route('/api/departments', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'receptionist')
def api_departments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Department POST data: {data}")  # Debug
            
            if not data or 'dept_name' not in data:
                return jsonify({'success': False, 'error': 'Missing department name'}), 400
            
            cursor.execute("INSERT INTO departments (dept_name, description) VALUES (%s, %s)",
                          (data['dept_name'], data.get('description', '')))
            conn.commit()
            print(f"Department added successfully: {data['dept_name']}")  # Debug
            conn.close()
            return jsonify({'success': True})
        except mysql.connector.IntegrityError as e:
            print(f"Department integrity error: {e}")  # Debug
            conn.close()
            return jsonify({'success': False, 'error': 'Department name already exists'}), 400
        except Exception as e:
            print(f"Department error: {e}")  # Debug
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    cursor.execute("SELECT * FROM departments ORDER BY dept_id")
    departments = cursor.fetchall()
    conn.close()
    return jsonify(departments)

@app.route('/api/departments/<int:dept_id>', methods=['PUT', 'DELETE'])
def api_department(dept_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        cursor.execute("UPDATE departments SET dept_name=%s, description=%s WHERE dept_id=%s",
                      (data['dept_name'], data['description'], dept_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        try:
            cursor.execute("DELETE FROM departments WHERE dept_id=%s", (dept_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        except mysql.connector.Error as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)})

# Doctors CRUD
@app.route('/doctors')
def doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.*, dept.dept_name 
        FROM doctors d 
        JOIN departments dept ON d.dept_id = dept.dept_id 
        ORDER BY d.doctor_id
    """)
    doctors = cursor.fetchall()
    
    cursor.execute("SELECT * FROM departments ORDER BY dept_id")
    departments = cursor.fetchall()
    conn.close()
    return render_template('doctors.html', doctors=doctors, departments=departments)

@app.route('/api/doctors', methods=['GET', 'POST'])
def api_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Doctor POST data: {data}")  # Debug
            
            required_fields = ['doctor_name', 'specialization', 'dept_id', 'phone', 'email']
            for field in required_fields:
                if not data or field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            cursor.execute("""
                INSERT INTO doctors (doctor_name, specialization, dept_id, phone, email) 
                VALUES (%s, %s, %s, %s, %s)
            """, (data['doctor_name'], data['specialization'], int(data['dept_id']), 
                  data['phone'], data['email']))
            conn.commit()
            print(f"Doctor added successfully: {data['doctor_name']}")  # Debug
            conn.close()
            return jsonify({'success': True})
        except mysql.connector.IntegrityError as e:
            print(f"Doctor integrity error: {e}")  # Debug
            conn.close()
            if 'phone' in str(e):
                return jsonify({'success': False, 'error': 'Phone number already exists'}), 400
            elif 'email' in str(e):
                return jsonify({'success': False, 'error': 'Email already exists'}), 400
            else:
                return jsonify({'success': False, 'error': 'Data constraint violation'}), 400
        except Exception as e:
            print(f"Doctor error: {e}")  # Debug
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    cursor.execute("""
        SELECT d.*, dept.dept_name 
        FROM doctors d 
        JOIN departments dept ON d.dept_id = dept.dept_id 
        ORDER BY d.doctor_id
    """)
    doctors = cursor.fetchall()
    conn.close()
    return jsonify(doctors)

@app.route('/api/doctors/<int:doctor_id>', methods=['PUT', 'DELETE'])
def api_doctor(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        cursor.execute("""
            UPDATE doctors SET doctor_name=%s, specialization=%s, dept_id=%s, phone=%s, email=%s 
            WHERE doctor_id=%s
        """, (data['doctor_name'], data['specialization'], data['dept_id'], 
              data['phone'], data['email'], doctor_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        try:
            cursor.execute("DELETE FROM doctors WHERE doctor_id=%s", (doctor_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        except mysql.connector.Error as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)})

# Patients CRUD
@app.route('/patients')
def patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY patient_id")
    patients = cursor.fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)

@app.route('/api/patients', methods=['GET', 'POST'])
def api_patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Patient POST data: {data}")  # Debug
            
            required_fields = ['patient_name', 'age', 'gender', 'phone']
            for field in required_fields:
                if not data or field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            cursor.execute("""
                INSERT INTO patients (patient_name, age, gender, phone, address) 
                VALUES (%s, %s, %s, %s, %s)
            """, (data['patient_name'], int(data['age']), data['gender'], 
                  data['phone'], data.get('address', '')))
            conn.commit()
            print(f"Patient added successfully: {data['patient_name']}")  # Debug
            conn.close()
            return jsonify({'success': True})
        except mysql.connector.IntegrityError as e:
            print(f"Patient integrity error: {e}")  # Debug
            conn.close()
            return jsonify({'success': False, 'error': 'Phone number already exists'}), 400
        except Exception as e:
            print(f"Patient error: {e}")  # Debug
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    cursor.execute("SELECT * FROM patients ORDER BY patient_id")
    patients = cursor.fetchall()
    conn.close()
    return jsonify(patients)

@app.route('/api/patients/<int:patient_id>', methods=['PUT', 'DELETE'])
def api_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        cursor.execute("""
            UPDATE patients SET patient_name=%s, age=%s, gender=%s, phone=%s, address=%s 
            WHERE patient_id=%s
        """, (data['patient_name'], data['age'], data['gender'], 
              data['phone'], data['address'], patient_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM patients WHERE patient_id=%s", (patient_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

# Queue Tokens CRUD
@app.route('/tokens')
def tokens():
    conn = get_db_connection()
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
    
    cursor.execute("SELECT * FROM patients ORDER BY patient_id")
    patients = cursor.fetchall()
    
    cursor.execute("SELECT * FROM doctors ORDER BY doctor_id")
    doctors = cursor.fetchall()
    
    cursor.execute("SELECT * FROM departments ORDER BY dept_id")
    departments = cursor.fetchall()
    
    conn.close()
    return render_template('tokens.html', tokens=tokens, patients=patients, 
                         doctors=doctors, departments=departments)

@app.route('/api/tokens', methods=['GET', 'POST'])
def api_tokens():
    if request.method == 'POST':
        conn = None
        try:
            data = request.get_json()
            print(f"\n=== TOKEN GENERATION REQUEST ===")
            print(f"Received data: {data}")
            print(f"Data type: {type(data)}")
            
            if not data:
                print("ERROR: No data received")
                return jsonify({'success': False, 'error': 'No data received'}), 400
            
            required_fields = ['patient_id', 'doctor_id', 'dept_id', 'appointment_time']
            for field in required_fields:
                if field not in data or not data[field]:
                    print(f"ERROR: Missing field: {field}")
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            print(f"All required fields present")
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Validate patient exists
            cursor.execute("SELECT patient_id, patient_name FROM patients WHERE patient_id = %s", (data['patient_id'],))
            patient = cursor.fetchone()
            if not patient:
                print(f"ERROR: Patient {data['patient_id']} not found")
                conn.close()
                return jsonify({'success': False, 'error': 'Patient not found'}), 400
            print(f"Patient found: {patient['patient_name']}")
            
            # Validate doctor exists
            cursor.execute("SELECT doctor_id, doctor_name FROM doctors WHERE doctor_id = %s", (data['doctor_id'],))
            doctor = cursor.fetchone()
            if not doctor:
                print(f"ERROR: Doctor {data['doctor_id']} not found")
                conn.close()
                return jsonify({'success': False, 'error': 'Doctor not found'}), 400
            print(f"Doctor found: {doctor['doctor_name']}")
            
            # Check for duplicate active tokens for same patient
            cursor.execute("""
                SELECT token_id, token_number FROM queue_tokens 
                WHERE patient_id = %s AND status IN ('Waiting', 'In Progress')
            """, (data['patient_id'],))
            existing = cursor.fetchone()
            if existing:
                print(f"ERROR: Patient already has active token: {existing['token_number']}")
                conn.close()
                return jsonify({'success': False, 'error': f'Patient already has an active token: {existing["token_number"]}'}), 400
            
            # Generate token number
            cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
            total_tokens = cursor.fetchone()['count']
            token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{(total_tokens + 1):04d}"
            print(f"Generated token number: {token_number}")
            
            # Insert token
            cursor.execute("""
                INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
                VALUES (%s, %s, %s, %s, %s, 'Waiting')
            """, (token_number, int(data['patient_id']), int(data['doctor_id']), int(data['dept_id']), 
                  data['appointment_time']))
            
            conn.commit()
            token_id = cursor.lastrowid
            print(f"SUCCESS: Token {token_number} created with ID {token_id}")
            print(f"=== END TOKEN GENERATION ===\n")
            
            conn.close()
            return jsonify({'success': True, 'token_number': token_number})
            
        except mysql.connector.Error as e:
            print(f"DATABASE ERROR: {e}")
            if conn:
                conn.close()
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
        except Exception as e:
            print(f"GENERAL ERROR: {e}")
            if conn:
                conn.close()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET request
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
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
    return jsonify(tokens)

@app.route('/api/tokens/<int:token_id>', methods=['PUT', 'DELETE'])
def api_token(token_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        cursor.execute("""
            UPDATE queue_tokens SET status=%s WHERE token_id=%s
        """, (data['status'], token_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM queue_tokens WHERE token_id=%s", (token_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

# Reports
@app.route('/reports')
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Department patient count
    cursor.execute("SELECT * FROM department_patient_count")
    dept_report = cursor.fetchall()
    
    # Doctor token count
    cursor.execute("SELECT * FROM doctor_token_count")
    doctor_report = cursor.fetchall()
    
    # Daily token summary
    cursor.execute("SELECT * FROM daily_token_summary LIMIT 10")
    daily_report = cursor.fetchall()
    
    conn.close()
    return render_template('reports.html', dept_report=dept_report, 
                         doctor_report=doctor_report, daily_report=daily_report)

if __name__ == '__main__':
    app.run(debug=True)