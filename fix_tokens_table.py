import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor()

# Create queue_tokens table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS queue_tokens (
        token_id INT PRIMARY KEY AUTO_INCREMENT,
        token_number VARCHAR(20) UNIQUE NOT NULL,
        patient_id INT NOT NULL,
        doctor_id INT NOT NULL,
        dept_id INT NOT NULL,
        appointment_time DATETIME NOT NULL,
        status ENUM('Waiting', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Waiting',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE RESTRICT,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
    )
""")

connection.commit()
print("queue_tokens table created successfully!")

cursor.close()
connection.close()
