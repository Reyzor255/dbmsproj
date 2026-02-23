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
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')

# DEPARTMENTS
@app.route('/departments')
def departments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departments ORDER BY dept_name")
    departments = cursor.fetchall()
    conn.close()
    return render_template('departments.html', departments=departments)

@app.route('/api/departments', methods=['GET', 'POST'])
def api_departments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        data = request.get_json()
        cursor.execute("INSERT INTO departments (dept_name, description) VALUES (%s, %s)",
                      (data['dept_name'], data['description']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    cursor.execute("SELECT * FROM departments ORDER BY dept_name")
    departments = cursor.fetchall()
    conn.close()
    return jsonify(departments)

@app.route('/api/departments/<int:dept_id>', methods=['PUT', 'DELETE'])
def api_department(dept_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.get_json()
        cursor.execute("UPDATE departments SET dept_name=%s, description=%s WHERE dept_id=%s",
                      (data['dept_name'], data['description'], dept_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM departments WHERE dept_id=%s", (dept_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

# DOCTORS
@app.route('/doctors')
def doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.*, dept.dept_name 
        FROM doctors d 
        JOIN departments dept ON d.dept_id = dept.dept_id 
        ORDER BY d.doctor_name
    """)
    doctors = cursor.fetchall()
    
    cursor.execute("SELECT * FROM departments ORDER BY dept_name")
    departments = cursor.fetchall()
    conn.close()
    return render_template('doctors.html', doctors=doctors, departments=departments)

@app.route('/api/doctors', methods=['GET', 'POST'])
def api_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        data = request.get_json()
        cursor.execute("""
            INSERT INTO doctors (doctor_name, specialization, dept_id, phone, email) 
            VALUES (%s, %s, %s, %s, %s)
        """, (data['doctor_name'], data['specialization'], data['dept_id'], 
              data['phone'], data['email']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    cursor.execute("""
        SELECT d.*, dept.dept_name 
        FROM doctors d 
        JOIN departments dept ON d.dept_id = dept.dept_id 
        ORDER BY d.doctor_name
    """)
    doctors = cursor.fetchall()
    conn.close()
    return jsonify(doctors)

@app.route('/api/doctors/<int:doctor_id>', methods=['PUT', 'DELETE'])
def api_doctor(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.get_json()
        cursor.execute("""
            UPDATE doctors SET doctor_name=%s, specialization=%s, dept_id=%s, phone=%s, email=%s 
            WHERE doctor_id=%s
        """, (data['doctor_name'], data['specialization'], data['dept_id'], 
              data['phone'], data['email'], doctor_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM doctors WHERE doctor_id=%s", (doctor_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

# PATIENTS
@app.route('/patients')
def patients():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients ORDER BY patient_name")
        patients = cursor.fetchall()
        conn.close()
        
        print(f"Found {len(patients)} patients for display")  # Debug log
        for patient in patients:
            print(f"Patient: {patient}")  # Debug log
            
        return render_template('patients_new.html', patients=patients)
    except Exception as e:
        print(f"Error in patients route: {e}")
        return render_template('patients_new.html', patients=[])

@app.route('/api/patients', methods=['GET', 'POST'])
def api_patients():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Received patient data: {data}")  # Debug log
            
            if not data:
                return jsonify({'success': False, 'error': 'No data received'}), 400
            
            # Validate required fields
            required_fields = ['patient_name', 'age', 'gender', 'phone']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                INSERT INTO patients (patient_name, age, gender, phone, address) 
                VALUES (%s, %s, %s, %s, %s)
            """, (data['patient_name'], data['age'], data['gender'], 
                  data['phone'], data.get('address', '')))
            
            conn.commit()
            patient_id = cursor.lastrowid
            conn.close()
            
            print(f"Patient added successfully with ID: {patient_id}")  # Debug log
            return jsonify({'success': True, 'patient_id': patient_id})
            
        except mysql.connector.IntegrityError as e:
            print(f"Database integrity error: {e}")  # Debug log
            if 'phone' in str(e):
                return jsonify({'success': False, 'error': 'Phone number already exists'}), 400
            return jsonify({'success': False, 'error': 'Database constraint violation'}), 400
        except mysql.connector.Error as e:
            print(f"Database error: {e}")  # Debug log
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
        except Exception as e:
            print(f"General error: {e}")  # Debug log
            return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500
    
    # GET request
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients ORDER BY patient_name")
        patients = cursor.fetchall()
        conn.close()
        return jsonify(patients)
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>', methods=['PUT', 'DELETE'])
def api_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.get_json()
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

# TOKENS
@app.route('/tokens')
def tokens():
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
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Generate token number
        cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
        total_tokens = cursor.fetchone()['count']
        token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{(total_tokens + 1):04d}"
        
        cursor.execute("""
            INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
            VALUES (%s, %s, %s, %s, %s, 'Waiting')
        """, (token_number, data['patient_id'], data['doctor_id'], data['dept_id'], 
              data['appointment_time']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'token_number': token_number})
    
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
        data = request.get_json()
        cursor.execute("UPDATE queue_tokens SET status=%s WHERE token_id=%s",
                      (data['status'], token_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM queue_tokens WHERE token_id=%s", (token_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

# REPORTS
@app.route('/reports')
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Department patient count
    cursor.execute("""
        SELECT 
            d.dept_name,
            COUNT(qt.token_id) as total_patients,
            COUNT(CASE WHEN qt.status = 'Waiting' THEN 1 END) as waiting_patients,
            COUNT(CASE WHEN qt.status = 'Completed' THEN 1 END) as completed_patients
        FROM departments d
        LEFT JOIN queue_tokens qt ON d.dept_id = qt.dept_id
        GROUP BY d.dept_id, d.dept_name
    """)
    dept_report = cursor.fetchall()
    
    # Doctor token count
    cursor.execute("""
        SELECT 
            d.doctor_name,
            dept.dept_name,
            COUNT(qt.token_id) as total_tokens,
            ROUND(AVG(CASE WHEN qt.status = 'Completed' THEN 1.0 ELSE 0.0 END) * 100, 2) as completion_rate
        FROM doctors d
        LEFT JOIN queue_tokens qt ON d.doctor_id = qt.doctor_id
        LEFT JOIN departments dept ON d.dept_id = dept.dept_id
        GROUP BY d.doctor_id, d.doctor_name, dept.dept_name
    """)
    doctor_report = cursor.fetchall()
    
    # Daily token summary
    cursor.execute("""
        SELECT 
            DATE(created_at) as token_date,
            COUNT(*) as tokens_generated,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_tokens,
            COUNT(CASE WHEN status = 'Waiting' THEN 1 END) as pending_tokens
        FROM queue_tokens
        GROUP BY DATE(created_at)
        ORDER BY token_date DESC
        LIMIT 10
    """)
    daily_report = cursor.fetchall()
    
    conn.close()
    return render_template('reports.html', dept_report=dept_report, 
                         doctor_report=doctor_report, daily_report=daily_report)

@app.route('/test-add-patient')
def test_add_patient():
    return render_template('test_add_patient.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)