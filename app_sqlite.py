from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
DB_FILE = 'hospital_queue.db'

def init_db():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript('''
        -- Departments table
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Doctors table
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_name VARCHAR(100) NOT NULL,
            specialization VARCHAR(100) NOT NULL,
            dept_id INTEGER NOT NULL,
            phone VARCHAR(15) UNIQUE,
            email VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        );

        -- Patients table
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL CHECK (age > 0 AND age <= 120),
            gender TEXT CHECK (gender IN ('Male', 'Female', 'Other')) NOT NULL,
            phone VARCHAR(15) UNIQUE NOT NULL,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Queue tokens table
        CREATE TABLE IF NOT EXISTS queue_tokens (
            token_id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_number VARCHAR(20) UNIQUE NOT NULL,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            dept_id INTEGER NOT NULL,
            appointment_time DATETIME NOT NULL,
            status TEXT CHECK (status IN ('Waiting', 'In Progress', 'Completed', 'Cancelled')) DEFAULT 'Waiting',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        );
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] == 0:
        cursor.executescript('''
            INSERT INTO departments (dept_name, description) VALUES
            ('Cardiology', 'Heart and cardiovascular system'),
            ('Neurology', 'Brain and nervous system'),
            ('Orthopedics', 'Bones and joints'),
            ('Pediatrics', 'Children healthcare');

            INSERT INTO doctors (doctor_name, specialization, dept_id, phone, email) VALUES
            ('Dr. John Smith', 'Cardiologist', 1, '1234567890', 'john.smith@hospital.com'),
            ('Dr. Sarah Johnson', 'Neurologist', 2, '1234567891', 'sarah.johnson@hospital.com'),
            ('Dr. Mike Wilson', 'Orthopedic Surgeon', 3, '1234567892', 'mike.wilson@hospital.com'),
            ('Dr. Emily Davis', 'Pediatrician', 4, '1234567893', 'emily.davis@hospital.com');

            INSERT INTO patients (patient_name, age, gender, phone, address) VALUES
            ('Alice Brown', 35, 'Female', '9876543210', '123 Main St'),
            ('Bob Green', 45, 'Male', '9876543211', '456 Oak Ave'),
            ('Carol White', 28, 'Female', '9876543212', '789 Pine Rd');
        ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_token_number(dept_id):
    """Generate unique token number"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get department name
    cursor.execute("SELECT dept_name FROM departments WHERE dept_id = ?", (dept_id,))
    dept_name = cursor.fetchone()['dept_name']
    dept_code = dept_name[:3].upper()
    
    # Get today's token count
    cursor.execute("""
        SELECT COUNT(*) as count FROM queue_tokens 
        WHERE dept_id = ? AND DATE(created_at) = DATE('now')
    """, (dept_id,))
    token_count = cursor.fetchone()['count'] + 1
    
    conn.close()
    
    from datetime import datetime
    date_str = datetime.now().strftime('%Y%m%d')
    return f"{dept_code}-{date_str}-{token_count:03d}"

# Initialize database on startup
init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/departments')
def departments():
    conn = get_db_connection()
    departments = conn.execute("SELECT * FROM departments ORDER BY dept_name").fetchall()
    conn.close()
    return render_template('departments.html', departments=departments)

@app.route('/api/departments', methods=['GET', 'POST'])
def api_departments():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.json
        conn.execute("INSERT INTO departments (dept_name, description) VALUES (?, ?)",
                    (data['dept_name'], data['description']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    departments = conn.execute("SELECT * FROM departments ORDER BY dept_name").fetchall()
    conn.close()
    return jsonify([dict(row) for row in departments])

@app.route('/api/departments/<int:dept_id>', methods=['PUT', 'DELETE'])
def api_department(dept_id):
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        conn.execute("UPDATE departments SET dept_name=?, description=? WHERE dept_id=?",
                    (data['dept_name'], data['description'], dept_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        try:
            conn.execute("DELETE FROM departments WHERE dept_id=?", (dept_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'error': str(e)})

@app.route('/doctors')
def doctors():
    conn = get_db_connection()
    doctors = conn.execute("""
        SELECT d.*, dept.dept_name 
        FROM doctors d 
        JOIN departments dept ON d.dept_id = dept.dept_id 
        ORDER BY d.doctor_name
    """).fetchall()
    
    departments = conn.execute("SELECT * FROM departments ORDER BY dept_name").fetchall()
    conn.close()
    return render_template('doctors.html', doctors=doctors, departments=departments)

@app.route('/api/doctors', methods=['GET', 'POST'])
def api_doctors():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.json
        conn.execute("""
            INSERT INTO doctors (doctor_name, specialization, dept_id, phone, email) 
            VALUES (?, ?, ?, ?, ?)
        """, (data['doctor_name'], data['specialization'], data['dept_id'], 
              data['phone'], data['email']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    doctors = conn.execute("""
        SELECT d.*, dept.dept_name 
        FROM doctors d 
        JOIN departments dept ON d.dept_id = dept.dept_id 
        ORDER BY d.doctor_name
    """).fetchall()
    conn.close()
    return jsonify([dict(row) for row in doctors])

@app.route('/patients')
def patients():
    conn = get_db_connection()
    patients = conn.execute("SELECT * FROM patients ORDER BY patient_name").fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)

@app.route('/api/patients', methods=['GET', 'POST'])
def api_patients():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.json
        conn.execute("""
            INSERT INTO patients (patient_name, age, gender, phone, address) 
            VALUES (?, ?, ?, ?, ?)
        """, (data['patient_name'], data['age'], data['gender'], 
              data['phone'], data['address']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    patients = conn.execute("SELECT * FROM patients ORDER BY patient_name").fetchall()
    conn.close()
    return jsonify([dict(row) for row in patients])

@app.route('/tokens')
def tokens():
    conn = get_db_connection()
    
    tokens = conn.execute("""
        SELECT qt.*, p.patient_name, d.doctor_name, dept.dept_name
        FROM queue_tokens qt
        JOIN patients p ON qt.patient_id = p.patient_id
        JOIN doctors d ON qt.doctor_id = d.doctor_id
        JOIN departments dept ON qt.dept_id = dept.dept_id
        ORDER BY qt.appointment_time
    """).fetchall()
    
    patients = conn.execute("SELECT * FROM patients ORDER BY patient_name").fetchall()
    doctors = conn.execute("SELECT * FROM doctors ORDER BY doctor_name").fetchall()
    departments = conn.execute("SELECT * FROM departments ORDER BY dept_name").fetchall()
    
    conn.close()
    return render_template('tokens.html', tokens=tokens, patients=patients, 
                         doctors=doctors, departments=departments)

@app.route('/api/tokens', methods=['GET', 'POST'])
def api_tokens():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.json
        token_number = generate_token_number(data['dept_id'])
        
        conn.execute("""
            INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time) 
            VALUES (?, ?, ?, ?, ?)
        """, (token_number, data['patient_id'], data['doctor_id'], data['dept_id'], 
              data['appointment_time']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    tokens = conn.execute("""
        SELECT qt.*, p.patient_name, d.doctor_name, dept.dept_name
        FROM queue_tokens qt
        JOIN patients p ON qt.patient_id = p.patient_id
        JOIN doctors d ON qt.doctor_id = d.doctor_id
        JOIN departments dept ON qt.dept_id = dept.dept_id
        ORDER BY qt.appointment_time
    """).fetchall()
    conn.close()
    return jsonify([dict(row) for row in tokens])

@app.route('/api/tokens/<int:token_id>', methods=['PUT', 'DELETE'])
def api_token(token_id):
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        conn.execute("UPDATE queue_tokens SET status=? WHERE token_id=?",
                    (data['status'], token_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        conn.execute("DELETE FROM queue_tokens WHERE token_id=?", (token_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/reports')
def reports():
    conn = get_db_connection()
    
    # Department patient count
    dept_report = conn.execute("""
        SELECT 
            d.dept_name,
            COUNT(qt.token_id) as total_patients,
            COUNT(CASE WHEN qt.status = 'Waiting' THEN 1 END) as waiting_patients,
            COUNT(CASE WHEN qt.status = 'Completed' THEN 1 END) as completed_patients
        FROM departments d
        LEFT JOIN queue_tokens qt ON d.dept_id = qt.dept_id
        GROUP BY d.dept_id, d.dept_name
    """).fetchall()
    
    # Doctor token count
    doctor_report = conn.execute("""
        SELECT 
            d.doctor_name,
            dept.dept_name,
            COUNT(qt.token_id) as total_tokens,
            ROUND(AVG(CASE WHEN qt.status = 'Completed' THEN 1.0 ELSE 0.0 END) * 100, 2) as completion_rate
        FROM doctors d
        LEFT JOIN queue_tokens qt ON d.doctor_id = qt.doctor_id
        LEFT JOIN departments dept ON d.dept_id = dept.dept_id
        GROUP BY d.doctor_id, d.doctor_name, dept.dept_name
    """).fetchall()
    
    # Daily token summary
    daily_report = conn.execute("""
        SELECT 
            DATE(created_at) as token_date,
            COUNT(*) as tokens_generated,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_tokens,
            COUNT(CASE WHEN status = 'Waiting' THEN 1 END) as pending_tokens
        FROM queue_tokens
        GROUP BY DATE(created_at)
        ORDER BY token_date DESC
        LIMIT 10
    """).fetchall()
    
    conn.close()
    return render_template('reports.html', dept_report=dept_report, 
                         doctor_report=doctor_report, daily_report=daily_report)

if __name__ == '__main__':
    app.run(debug=True)