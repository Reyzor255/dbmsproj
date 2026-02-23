import mysql.connector

# Database configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

# Sample patients data
patients = [
    ('Alice Brown', 35, 'Female', '9876543210', '123 Main St'),
    ('Bob Green', 45, 'Male', '9876543211', '456 Oak Ave'),
    ('Carol White', 28, 'Female', '9876543212', '789 Pine Rd'),
    ('David Johnson', 52, 'Male', '9876543213', '321 Elm St'),
    ('Emma Wilson', 29, 'Female', '9876543214', '654 Maple Dr'),
    ('Frank Miller', 38, 'Male', '9876543215', '987 Cedar Ln'),
    ('Grace Davis', 41, 'Female', '9876543216', '147 Birch Ave'),
    ('Henry Taylor', 33, 'Male', '9876543217', '258 Spruce St'),
    ('Ivy Anderson', 27, 'Female', '9876543218', '369 Willow Rd'),
    ('Jack Thompson', 46, 'Male', '9876543219', '741 Pine Ave')
]

try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    # Clear existing patients (optional)
    print("Clearing existing patients...")
    cursor.execute("DELETE FROM patients")
    
    # Insert new patients
    print("Adding new patients...")
    for patient in patients:
        cursor.execute("""
            INSERT INTO patients (patient_name, age, gender, phone, address) 
            VALUES (%s, %s, %s, %s, %s)
        """, patient)
        print(f"Added: {patient[0]}")
    
    connection.commit()
    print(f"\nSuccessfully added {len(patients)} patients!")
    
    # Verify the data
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    print(f"Total patients in database: {count}")
    
except mysql.connector.Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Database connection closed.")