import mysql.connector
from datetime import datetime, timedelta

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    
    print("=== TESTING TOKEN GENERATION ===\n")
    
    # Check if we have patients
    cursor.execute("SELECT * FROM patients LIMIT 1")
    patient = cursor.fetchone()
    if not patient:
        print("ERROR: No patients found in database!")
        exit(1)
    print(f"Found patient: {patient['patient_name']} (ID: {patient['patient_id']})")
    
    # Check if we have doctors
    cursor.execute("SELECT * FROM doctors LIMIT 1")
    doctor = cursor.fetchone()
    if not doctor:
        print("ERROR: No doctors found in database!")
        exit(1)
    print(f"Found doctor: {doctor['doctor_name']} (ID: {doctor['doctor_id']})")
    
    # Check if we have departments
    cursor.execute("SELECT * FROM departments LIMIT 1")
    department = cursor.fetchone()
    if not department:
        print("ERROR: No departments found in database!")
        exit(1)
    print(f"Found department: {department['dept_name']} (ID: {department['dept_id']})")
    
    # Generate token number
    cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
    total_tokens = cursor.fetchone()['count']
    token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{(total_tokens + 1):04d}"
    print(f"\nGenerated token number: {token_number}")
    
    # Create appointment time (1 hour from now)
    appointment_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Appointment time: {appointment_time}")
    
    # Try to insert token
    print("\nAttempting to insert token...")
    cursor.execute("""
        INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
        VALUES (%s, %s, %s, %s, %s, 'Waiting')
    """, (token_number, patient['patient_id'], doctor['doctor_id'], department['dept_id'], appointment_time))
    
    connection.commit()
    token_id = cursor.lastrowid
    
    print(f"SUCCESS: Token inserted with ID: {token_id}")
    
    # Verify the token
    cursor.execute("""
        SELECT qt.*, p.patient_name, d.doctor_name, dept.dept_name
        FROM queue_tokens qt
        JOIN patients p ON qt.patient_id = p.patient_id
        JOIN doctors d ON qt.doctor_id = d.doctor_id
        JOIN departments dept ON qt.dept_id = dept.dept_id
        WHERE qt.token_id = %s
    """, (token_id,))
    
    token = cursor.fetchone()
    print(f"\nToken Details:")
    print(f"  Token Number: {token['token_number']}")
    print(f"  Patient: {token['patient_name']}")
    print(f"  Doctor: {token['doctor_name']}")
    print(f"  Department: {token['dept_name']}")
    print(f"  Status: {token['status']}")
    
    print("\n=== TOKEN GENERATION TEST PASSED ===")
    
except mysql.connector.Error as e:
    print(f"\nDATABASE ERROR: {e}")
except Exception as e:
    print(f"\nERROR: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()