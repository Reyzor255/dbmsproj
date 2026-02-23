import mysql.connector
from mysql.connector import Error

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS queue_tokens")
    cursor.execute("DROP TABLE IF EXISTS doctors")
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS departments")
    
    # Create departments table
    cursor.execute("""
        CREATE TABLE departments (
            dept_id INT PRIMARY KEY AUTO_INCREMENT,
            dept_name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Created departments table")
    
    # Create doctors table
    cursor.execute("""
        CREATE TABLE doctors (
            doctor_id INT PRIMARY KEY AUTO_INCREMENT,
            doctor_name VARCHAR(100) NOT NULL,
            specialization VARCHAR(100) NOT NULL,
            dept_id INT NOT NULL,
            phone VARCHAR(15) UNIQUE,
            email VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        )
    """)
    print("Created doctors table")
    
    # Create patients table
    cursor.execute("""
        CREATE TABLE patients (
            patient_id INT PRIMARY KEY AUTO_INCREMENT,
            patient_name VARCHAR(100) NOT NULL,
            age INT NOT NULL CHECK (age > 0 AND age <= 120),
            gender ENUM('Male', 'Female', 'Other') NOT NULL,
            phone VARCHAR(15) UNIQUE NOT NULL,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Created patients table")
    
    # Create queue_tokens table
    cursor.execute("""
        CREATE TABLE queue_tokens (
            token_id INT PRIMARY KEY AUTO_INCREMENT,
            token_number VARCHAR(20) UNIQUE NOT NULL,
            patient_id INT NOT NULL,
            doctor_id INT NOT NULL,
            dept_id INT NOT NULL,
            appointment_time DATETIME NOT NULL,
            status ENUM('Waiting', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Waiting',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        )
    """)
    print("Created queue_tokens table")
    
    # Insert sample data
    cursor.execute("""
        INSERT INTO departments (dept_name, description) VALUES
        ('Cardiology', 'Heart and cardiovascular system'),
        ('Neurology', 'Brain and nervous system'),
        ('Orthopedics', 'Bones and joints'),
        ('Pediatrics', 'Children healthcare')
    """)
    
    cursor.execute("""
        INSERT INTO doctors (doctor_name, specialization, dept_id, phone, email) VALUES
        ('Dr. John Smith', 'Cardiologist', 1, '1234567890', 'john.smith@hospital.com'),
        ('Dr. Sarah Johnson', 'Neurologist', 2, '1234567891', 'sarah.johnson@hospital.com'),
        ('Dr. Mike Wilson', 'Orthopedic Surgeon', 3, '1234567892', 'mike.wilson@hospital.com'),
        ('Dr. Emily Davis', 'Pediatrician', 4, '1234567893', 'emily.davis@hospital.com')
    """)
    
    cursor.execute("""
        INSERT INTO patients (patient_name, age, gender, phone, address) VALUES
        ('Alice Brown', 35, 'Female', '9876543210', '123 Main St'),
        ('Bob Green', 45, 'Male', '9876543211', '456 Oak Ave'),
        ('Carol White', 28, 'Female', '9876543212', '789 Pine Rd')
    """)
    
    # Create views
    cursor.execute("""
        CREATE VIEW department_patient_count AS
        SELECT 
            d.dept_name,
            COUNT(qt.token_id) as total_patients,
            COUNT(CASE WHEN qt.status = 'Waiting' THEN 1 END) as waiting_patients,
            COUNT(CASE WHEN qt.status = 'Completed' THEN 1 END) as completed_patients
        FROM departments d
        LEFT JOIN queue_tokens qt ON d.dept_id = qt.dept_id
        GROUP BY d.dept_id, d.dept_name
    """)
    
    cursor.execute("""
        CREATE VIEW doctor_token_count AS
        SELECT 
            d.doctor_name,
            dept.dept_name,
            COUNT(qt.token_id) as total_tokens,
            AVG(CASE WHEN qt.status = 'Completed' THEN 1 ELSE 0 END) * 100 as completion_rate
        FROM doctors d
        LEFT JOIN queue_tokens qt ON d.doctor_id = qt.doctor_id
        LEFT JOIN departments dept ON d.dept_id = dept.dept_id
        GROUP BY d.doctor_id, d.doctor_name, dept.dept_name
    """)
    
    cursor.execute("""
        CREATE VIEW daily_token_summary AS
        SELECT 
            DATE(created_at) as token_date,
            COUNT(*) as tokens_generated,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_tokens,
            COUNT(CASE WHEN status = 'Waiting' THEN 1 END) as pending_tokens
        FROM queue_tokens
        GROUP BY DATE(created_at)
        ORDER BY token_date DESC
    """)
    
    connection.commit()
    print("Database setup completed successfully!")
    print("Sample data inserted")
    
except Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()