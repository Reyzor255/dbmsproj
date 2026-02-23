import mysql.connector
from mysql.connector import Error

# Database configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!'
}

try:
    # Connect to MySQL server
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS hospital_queue_db")
    print("Database 'hospital_queue_db' created successfully")
    
    # Use the database
    cursor.execute("USE hospital_queue_db")
    
    # Read and execute schema
    with open('database_schema.sql', 'r') as file:
        sql_script = file.read()
    
    # Split and execute statements
    statements = sql_script.split(';')
    for statement in statements:
        if statement.strip():
            try:
                cursor.execute(statement)
            except Error as e:
                if "already exists" not in str(e).lower():
                    print(f"Warning: {e}")
    
    connection.commit()
    print("Database schema created successfully")
    print("Sample data inserted")
    
except Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed")