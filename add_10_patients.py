import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor()

new_patients = [
    ('Daniel Thompson', 37, 'Male', '5551112222', '111 Cherry Lane'),
    ('Sophia Martinez', 25, 'Female', '5552223333', '222 Peach Street'),
    ('Oliver Harris', 50, 'Male', '5553334444', '333 Apple Avenue'),
    ('Isabella Clark', 32, 'Female', '5554445555', '444 Orange Drive'),
    ('Ethan Lewis', 41, 'Male', '5555556666', '555 Grape Road'),
    ('Mia Robinson', 28, 'Female', '5556667777', '666 Plum Court'),
    ('Lucas Walker', 45, 'Male', '5557778888', '777 Lemon Way'),
    ('Ava Young', 36, 'Female', '5558889999', '888 Lime Circle'),
    ('Mason King', 53, 'Male', '5559990000', '999 Berry Place'),
    ('Charlotte Wright', 29, 'Female', '5550001111', '1010 Melon Boulevard')
]

print("Adding 10 new patients...\n")

for patient in new_patients:
    cursor.execute("""
        INSERT INTO patients (patient_name, age, gender, phone, address) 
        VALUES (%s, %s, %s, %s, %s)
    """, patient)
    connection.commit()
    print(f"Added: {patient[0]}")

cursor.execute("SELECT COUNT(*) as count FROM patients")
total = cursor.fetchone()[0]
print(f"\nTotal patients: {total}")

cursor.close()
connection.close()
