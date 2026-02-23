import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor()

# Create users table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        role ENUM('admin', 'doctor', 'receptionist') NOT NULL,
        email VARCHAR(100) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert default users
cursor.execute("""
    INSERT INTO users (username, password, full_name, role, email) VALUES
    ('admin', 'admin123', 'System Administrator', 'admin', 'admin@hospital.com'),
    ('doctor1', 'doctor123', 'Dr. John Smith', 'doctor', 'john.smith@hospital.com'),
    ('reception', 'reception123', 'Reception Desk', 'receptionist', 'reception@hospital.com')
""")

connection.commit()
print("Users table created successfully!")
print("\nDefault Users:")
print("1. Username: admin, Password: admin123, Role: admin")
print("2. Username: doctor1, Password: doctor123, Role: doctor")
print("3. Username: reception, Password: reception123, Role: receptionist")

cursor.close()
connection.close()
