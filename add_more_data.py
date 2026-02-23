import mysql.connector
from datetime import datetime, timedelta
import random

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    
    print("=== ADDING MORE PATIENTS AND TOKENS ===\n")
    
    # Add more patients
    new_patients = [
        ('Michael Brown', 42, 'Male', '5551234567', '100 Oak Street'),
        ('Sarah Davis', 31, 'Female', '5552345678', '200 Pine Avenue'),
        ('James Wilson', 55, 'Male', '5553456789', '300 Maple Drive'),
        ('Emily Martinez', 26, 'Female', '5554567890', '400 Cedar Lane'),
        ('Robert Garcia', 48, 'Male', '5555678901', '500 Birch Road'),
        ('Linda Rodriguez', 39, 'Female', '5556789012', '600 Elm Court'),
        ('William Lee', 61, 'Male', '5557890123', '700 Ash Boulevard'),
        ('Patricia Walker', 34, 'Female', '5558901234', '800 Willow Way'),
        ('John Hall', 44, 'Male', '5559012345', '900 Spruce Circle'),
        ('Jennifer Allen', 29, 'Female', '5550123456', '1000 Fir Place')
    ]
    
    print("Adding new patients...")
    patient_ids = []
    for patient in new_patients:
        try:
            cursor.execute("""
                INSERT INTO patients (patient_name, age, gender, phone, address) 
                VALUES (%s, %s, %s, %s, %s)
            """, patient)
            connection.commit()
            patient_ids.append(cursor.lastrowid)
            print(f"  Added: {patient[0]}")
        except mysql.connector.IntegrityError:
            print(f"  Skipped: {patient[0]} (already exists)")
    
    # Get all patients, doctors, and departments
    cursor.execute("SELECT patient_id, patient_name FROM patients")
    all_patients = cursor.fetchall()
    
    cursor.execute("SELECT doctor_id, doctor_name FROM doctors")
    all_doctors = cursor.fetchall()
    
    cursor.execute("SELECT dept_id, dept_name FROM departments")
    all_departments = cursor.fetchall()
    
    print(f"\nTotal patients: {len(all_patients)}")
    print(f"Total doctors: {len(all_doctors)}")
    print(f"Total departments: {len(all_departments)}")
    
    # Generate tokens with different statuses
    statuses = ['Waiting', 'In Progress', 'Completed', 'Cancelled']
    
    print("\nGenerating tokens...")
    
    # Get current token count
    cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
    token_count = cursor.fetchone()['count']
    
    # Generate 15 tokens
    for i in range(15):
        patient = random.choice(all_patients)
        doctor = random.choice(all_doctors)
        department = random.choice(all_departments)
        
        # Check if patient already has an active token
        cursor.execute("""
            SELECT token_id FROM queue_tokens 
            WHERE patient_id = %s AND status IN ('Waiting', 'In Progress')
        """, (patient['patient_id'],))
        
        if cursor.fetchone():
            continue  # Skip if patient has active token
        
        # Generate token number
        token_count += 1
        token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{token_count:04d}"
        
        # Random appointment time (between yesterday and tomorrow)
        hours_offset = random.randint(-24, 24)
        appointment_time = (datetime.now() + timedelta(hours=hours_offset)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Assign status based on appointment time
        if hours_offset < -2:
            status = random.choice(['Completed', 'Cancelled'])
        elif hours_offset < 0:
            status = random.choice(['In Progress', 'Completed'])
        else:
            status = 'Waiting'
        
        cursor.execute("""
            INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (token_number, patient['patient_id'], doctor['doctor_id'], department['dept_id'], 
              appointment_time, status))
        
        connection.commit()
        print(f"  {token_number}: {patient['patient_name']} -> {doctor['doctor_name']} ({status})")
    
    # Show summary
    print("\n=== SUMMARY ===")
    cursor.execute("SELECT COUNT(*) as count FROM patients")
    print(f"Total Patients: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
    print(f"Total Tokens: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT status, COUNT(*) as count FROM queue_tokens GROUP BY status")
    print("\nTokens by Status:")
    for row in cursor.fetchall():
        print(f"  {row['status']}: {row['count']}")
    
    print("\n=== DATA ADDED SUCCESSFULLY ===")
    
except mysql.connector.Error as e:
    print(f"\nDATABASE ERROR: {e}")
except Exception as e:
    print(f"\nERROR: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()