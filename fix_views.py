import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor()

# Create views
cursor.execute("""
    CREATE OR REPLACE VIEW department_patient_count AS
    SELECT 
        d.dept_name,
        COUNT(qt.token_id) as total_patients,
        COUNT(CASE WHEN qt.status = 'Waiting' THEN 1 END) as waiting_patients,
        COUNT(CASE WHEN qt.status = 'Completed' THEN 1 END) as completed_patients
    FROM departments d
    LEFT JOIN queue_tokens qt ON d.dept_id = qt.dept_id
    GROUP BY d.dept_id, d.dept_name
""")

cursor.execute("""
    CREATE OR REPLACE VIEW doctor_token_count AS
    SELECT 
        d.doctor_name,
        dept.dept_name,
        COUNT(qt.token_id) as total_tokens,
        AVG(CASE WHEN qt.status = 'Completed' THEN 1 ELSE 0 END) * 100 as completion_rate
    FROM doctors d
    LEFT JOIN queue_tokens qt ON d.doctor_id = qt.doctor_id
    LEFT JOIN departments dept ON d.dept_id = dept.dept_id
    GROUP BY d.doctor_id, d.doctor_name, dept.dept_name
""")

cursor.execute("""
    CREATE OR REPLACE VIEW daily_token_summary AS
    SELECT 
        DATE(created_at) as token_date,
        COUNT(*) as tokens_generated,
        COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_tokens,
        COUNT(CASE WHEN status = 'Waiting' THEN 1 END) as pending_tokens
    FROM queue_tokens
    GROUP BY DATE(created_at)
    ORDER BY token_date DESC
""")

connection.commit()
print("All views created successfully!")

cursor.close()
connection.close()
