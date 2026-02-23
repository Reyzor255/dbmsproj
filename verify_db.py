import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    
    print("=== DATABASE VERIFICATION ===\n")
    
    # Check departments
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    print(f"DEPARTMENTS ({len(departments)}):")
    for dept in departments:
        print(f"  {dept['dept_id']}: {dept['dept_name']} - {dept['description']}")
    
    # Check doctors
    cursor.execute("""
        SELECT d.*, dept.dept_name 
        FROM doctors d 
        JOIN departments dept ON d.dept_id = dept.dept_id
    """)
    doctors = cursor.fetchall()
    print(f"\nDOCTORS ({len(doctors)}):")
    for doc in doctors:
        print(f"  {doc['doctor_id']}: {doc['doctor_name']} ({doc['specialization']}) - {doc['dept_name']}")
    
    # Check patients
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    print(f"\nPATIENTS ({len(patients)}):")
    for pat in patients:
        print(f"  {pat['patient_id']}: {pat['patient_name']} ({pat['age']}, {pat['gender']}) - {pat['phone']}")
    
    # Check tokens
    cursor.execute("""
        SELECT qt.*, p.patient_name, d.doctor_name, dept.dept_name
        FROM queue_tokens qt
        JOIN patients p ON qt.patient_id = p.patient_id
        JOIN doctors d ON qt.doctor_id = d.doctor_id
        JOIN departments dept ON qt.dept_id = dept.dept_id
    """)
    tokens = cursor.fetchall()
    print(f"\nTOKENS ({len(tokens)}):")
    for token in tokens:
        print(f"  {token['token_number']}: {token['patient_name']} -> {token['doctor_name']} ({token['status']})")
    
    print(f"\n=== SUMMARY ===")
    print(f"Departments: {len(departments)}")
    print(f"Doctors: {len(doctors)}")
    print(f"Patients: {len(patients)}")
    print(f"Tokens: {len(tokens)}")
    print("\nDatabase is ready for use!")
    
except mysql.connector.Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()