import mysql.connector
from datetime import datetime, timedelta
import random

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor(dictionary=True)

# Add 12 new patients
new_patients = [
    ('Alexander Scott', 43, 'Male', '5551231234', '1111 Oak Street'),
    ('Victoria Green', 31, 'Female', '5552342345', '1212 Pine Avenue'),
    ('Benjamin Adams', 38, 'Male', '5553453456', '1313 Maple Drive'),
    ('Amelia Baker', 27, 'Female', '5554564567', '1414 Cedar Lane'),
    ('Sebastian Nelson', 49, 'Male', '5555675678', '1515 Birch Road'),
    ('Harper Carter', 35, 'Female', '5556786789', '1616 Elm Court'),
    ('Jackson Mitchell', 42, 'Male', '5557897890', '1717 Ash Way'),
    ('Evelyn Perez', 30, 'Female', '5558908901', '1818 Willow Circle'),
    ('Logan Roberts', 46, 'Male', '5559019012', '1919 Spruce Place'),
    ('Abigail Turner', 33, 'Female', '5550120123', '2020 Fir Boulevard'),
    ('Noah Phillips', 39, 'Male', '5551231235', '2121 Poplar Street'),
    ('Emily Campbell', 26, 'Female', '5552342346', '2222 Hickory Avenue')
]

print("Adding 12 new patients...\n")
for patient in new_patients:
    cursor.execute("""
        INSERT INTO patients (patient_name, age, gender, phone, address) 
        VALUES (%s, %s, %s, %s, %s)
    """, patient)
    connection.commit()
    print(f"Added: {patient[0]}")

# Get all patients, doctors, departments
cursor.execute("SELECT patient_id, patient_name FROM patients ORDER BY patient_id")
all_patients = cursor.fetchall()

cursor.execute("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_id")
all_doctors = cursor.fetchall()

cursor.execute("SELECT dept_id FROM departments ORDER BY dept_id")
all_departments = cursor.fetchall()

# Get current token count
cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
token_count = cursor.fetchone()['count']

print("\nAdding 15 new tokens...\n")

# 10 Completed tokens
for i in range(10):
    patient = all_patients[i % len(all_patients)]
    doctor = random.choice(all_doctors)
    department = random.choice(all_departments)
    
    token_count += 1
    token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{token_count:04d}"
    appointment_time = (datetime.now() - timedelta(hours=random.randint(5, 48))).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
        VALUES (%s, %s, %s, %s, %s, 'Completed')
    """, (token_number, patient['patient_id'], doctor['doctor_id'], department['dept_id'], appointment_time))
    connection.commit()
    print(f"{token_number}: {patient['patient_name']} -> {doctor['doctor_name']} (Completed)")

# 2 Waiting tokens
for i in range(2):
    patient = all_patients[(i + 10) % len(all_patients)]
    doctor = random.choice(all_doctors)
    department = random.choice(all_departments)
    
    token_count += 1
    token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{token_count:04d}"
    appointment_time = (datetime.now() + timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
        VALUES (%s, %s, %s, %s, %s, 'Waiting')
    """, (token_number, patient['patient_id'], doctor['doctor_id'], department['dept_id'], appointment_time))
    connection.commit()
    print(f"{token_number}: {patient['patient_name']} -> {doctor['doctor_name']} (Waiting)")

# 3 In Progress tokens
for i in range(3):
    patient = all_patients[(i + 12) % len(all_patients)]
    doctor = random.choice(all_doctors)
    department = random.choice(all_departments)
    
    token_count += 1
    token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{token_count:04d}"
    appointment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
        VALUES (%s, %s, %s, %s, %s, 'In Progress')
    """, (token_number, patient['patient_id'], doctor['doctor_id'], department['dept_id'], appointment_time))
    connection.commit()
    print(f"{token_number}: {patient['patient_name']} -> {doctor['doctor_name']} (In Progress)")

# Summary
cursor.execute("SELECT COUNT(*) as count FROM patients")
print(f"\nTotal Patients: {cursor.fetchone()['count']}")

cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
print(f"Total Tokens: {cursor.fetchone()['count']}")

cursor.execute("SELECT status, COUNT(*) as count FROM queue_tokens GROUP BY status ORDER BY status")
print("\nTokens by Status:")
for row in cursor.fetchall():
    print(f"  {row['status']}: {row['count']}")

cursor.close()
connection.close()
print("\nDone!")
