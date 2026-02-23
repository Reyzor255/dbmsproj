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
    
    print("=== ADDING MORE DEPARTMENTS AND DOCTORS ===\n")
    
    # Add more departments
    new_departments = [
        ('Dermatology', 'Skin and related conditions'),
        ('Ophthalmology', 'Eye care and vision'),
        ('ENT', 'Ear, Nose, and Throat'),
        ('Psychiatry', 'Mental health and behavioral disorders'),
        ('Radiology', 'Medical imaging and diagnostics'),
        ('Emergency', 'Emergency and urgent care')
    ]
    
    print("Adding new departments...")
    dept_ids = {}
    for dept in new_departments:
        try:
            cursor.execute("""
                INSERT INTO departments (dept_name, description) 
                VALUES (%s, %s)
            """, dept)
            connection.commit()
            dept_ids[dept[0]] = cursor.lastrowid
            print(f"  Added: {dept[0]}")
        except mysql.connector.IntegrityError:
            # Department already exists, get its ID
            cursor.execute("SELECT dept_id FROM departments WHERE dept_name = %s", (dept[0],))
            result = cursor.fetchone()
            if result:
                dept_ids[dept[0]] = result['dept_id']
            print(f"  Skipped: {dept[0]} (already exists)")
    
    # Get all department IDs
    cursor.execute("SELECT dept_id, dept_name FROM departments")
    all_depts = {row['dept_name']: row['dept_id'] for row in cursor.fetchall()}
    
    # Add more doctors
    new_doctors = [
        ('Dr. Amanda Chen', 'Dermatologist', 'Dermatology', '1234567894', 'amanda.chen@hospital.com'),
        ('Dr. Robert Taylor', 'Ophthalmologist', 'Ophthalmology', '1234567895', 'robert.taylor@hospital.com'),
        ('Dr. Lisa Anderson', 'ENT Specialist', 'ENT', '1234567896', 'lisa.anderson@hospital.com'),
        ('Dr. David Martinez', 'Psychiatrist', 'Psychiatry', '1234567897', 'david.martinez@hospital.com'),
        ('Dr. Jennifer White', 'Radiologist', 'Radiology', '1234567898', 'jennifer.white@hospital.com'),
        ('Dr. Michael Brown', 'Emergency Physician', 'Emergency', '1234567899', 'michael.brown@hospital.com'),
        ('Dr. Patricia Garcia', 'Cardiologist', 'Cardiology', '1234567900', 'patricia.garcia@hospital.com'),
        ('Dr. James Rodriguez', 'Neurologist', 'Neurology', '1234567901', 'james.rodriguez@hospital.com'),
        ('Dr. Maria Lopez', 'Orthopedic Surgeon', 'Orthopedics', '1234567902', 'maria.lopez@hospital.com'),
        ('Dr. Christopher Lee', 'Pediatrician', 'Pediatrics', '1234567903', 'christopher.lee@hospital.com')
    ]
    
    print("\nAdding new doctors...")
    for doctor in new_doctors:
        try:
            dept_id = all_depts.get(doctor[2])
            if not dept_id:
                print(f"  Skipped: {doctor[0]} (department {doctor[2]} not found)")
                continue
            
            cursor.execute("""
                INSERT INTO doctors (doctor_name, specialization, dept_id, phone, email) 
                VALUES (%s, %s, %s, %s, %s)
            """, (doctor[0], doctor[1], dept_id, doctor[3], doctor[4]))
            connection.commit()
            print(f"  Added: {doctor[0]} ({doctor[1]}) - {doctor[2]}")
        except mysql.connector.IntegrityError as e:
            if 'phone' in str(e):
                print(f"  Skipped: {doctor[0]} (phone number already exists)")
            elif 'email' in str(e):
                print(f"  Skipped: {doctor[0]} (email already exists)")
            else:
                print(f"  Skipped: {doctor[0]} (already exists)")
    
    # Show summary
    print("\n=== SUMMARY ===")
    cursor.execute("SELECT COUNT(*) as count FROM departments")
    print(f"Total Departments: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM doctors")
    print(f"Total Doctors: {cursor.fetchone()['count']}")
    
    print("\nDoctors by Department:")
    cursor.execute("""
        SELECT dept.dept_name, COUNT(d.doctor_id) as doctor_count
        FROM departments dept
        LEFT JOIN doctors d ON dept.dept_id = d.dept_id
        GROUP BY dept.dept_id, dept.dept_name
        ORDER BY dept.dept_name
    """)
    for row in cursor.fetchall():
        print(f"  {row['dept_name']}: {row['doctor_count']} doctor(s)")
    
    print("\n=== DATA ADDED SUCCESSFULLY ===")
    
except mysql.connector.Error as e:
    print(f"\nDATABASE ERROR: {e}")
except Exception as e:
    print(f"\nERROR: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()