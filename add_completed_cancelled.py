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

# Get current token count
cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
token_count = cursor.fetchone()['count']

# Get patients without active tokens
cursor.execute("""
    SELECT p.patient_id, p.patient_name 
    FROM patients p
    WHERE p.patient_id NOT IN (
        SELECT patient_id FROM queue_tokens 
        WHERE status IN ('Waiting', 'In Progress')
    )
    ORDER BY p.patient_id
""")
available_patients = cursor.fetchall()

# Get all doctors and departments
cursor.execute("SELECT doctor_id, doctor_name FROM doctors ORDER BY doctor_id")
doctors = cursor.fetchall()

cursor.execute("SELECT dept_id FROM departments ORDER BY dept_id")
departments = cursor.fetchall()

print("Adding more Completed and Cancelled tokens...\n")

# Add 10 more tokens (5 completed, 5 cancelled)
statuses = ['Completed'] * 5 + ['Cancelled'] * 5
random.shuffle(statuses)

for i in range(10):
    if not available_patients:
        break
    
    patient = available_patients[i % len(available_patients)]
    doctor = random.choice(doctors)
    department = random.choice(departments)
    
    token_count += 1
    token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{token_count:04d}"
    
    # Past appointment time
    hours_ago = random.randint(3, 48)
    appointment_time = (datetime.now() - timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, appointment_time, status) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (token_number, patient['patient_id'], doctor['doctor_id'], department['dept_id'], 
          appointment_time, statuses[i]))
    
    connection.commit()
    print(f"{token_number}: {patient['patient_name']} -> {doctor['doctor_name']} ({statuses[i]})")

# Show summary
cursor.execute("SELECT status, COUNT(*) as count FROM queue_tokens GROUP BY status ORDER BY status")
print("\nTokens by Status:")
for row in cursor.fetchall():
    print(f"  {row['status']}: {row['count']}")

print(f"\nTotal Tokens: {token_count}")

cursor.close()
connection.close()
print("\nDone!")