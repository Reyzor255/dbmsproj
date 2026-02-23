import mysql.connector
from mysql.connector import Error

# Common password configurations to try
passwords = ['', 'root', 'password', 'admin', '123456']

print("Testing MySQL connection with different passwords...")

for pwd in passwords:
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=pwd
        )
        if connection.is_connected():
            print(f"✓ SUCCESS: Connected with password: '{pwd}'")
            
            # Try to create database
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS hospital_queue_db")
            print("✓ Database 'hospital_queue_db' created/verified")
            
            connection.close()
            
            # Update app.py with correct password
            with open('app.py', 'r') as f:
                content = f.read()
            
            content = content.replace("'password': '',", f"'password': '{pwd}',")
            
            with open('app.py', 'w') as f:
                f.write(content)
            
            print(f"✓ Updated app.py with correct password: '{pwd}'")
            break
            
    except Error as e:
        print(f"✗ Failed with password '{pwd}': {e}")

print("\nIf none worked, you may need to:")
print("1. Check if MySQL is running: 'net start mysql' or 'mysqld --console'")
print("2. Reset MySQL root password")
print("3. Use MySQL Workbench to connect and check credentials")