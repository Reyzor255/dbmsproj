import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor(dictionary=True)

print("Resetting patient IDs to start from 101...\n")

# Get all patients ordered by current ID
cursor.execute("SELECT * FROM patients ORDER BY patient_id")
patients = cursor.fetchall()

# Temporarily disable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

# Delete all patients
cursor.execute("DELETE FROM patients")

# Reset auto increment to 101
cursor.execute("ALTER TABLE patients AUTO_INCREMENT = 101")

# Re-insert patients (they will get new IDs starting from 101)
new_id = 101
old_to_new_id = {}

for patient in patients:
    cursor.execute("""
        INSERT INTO patients (patient_name, age, gender, phone, address) 
        VALUES (%s, %s, %s, %s, %s)
    """, (patient['patient_name'], patient['age'], patient['gender'], 
          patient['phone'], patient['address']))
    
    old_to_new_id[patient['patient_id']] = new_id
    print(f"Patient ID {patient['patient_id']} -> {new_id}: {patient['patient_name']}")
    new_id += 1

connection.commit()

# Update queue_tokens with new patient IDs
print("\nUpdating tokens with new patient IDs...")
for old_id, new_id in old_to_new_id.items():
    cursor.execute("UPDATE queue_tokens SET patient_id = %s WHERE patient_id = %s", (new_id, old_id))

connection.commit()

# Re-enable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

print("\nDone! Patient IDs now start from 101")

cursor.close()
connection.close()