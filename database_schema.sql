-- Hospital Queue Token Management System Database Schema

-- Create database
CREATE DATABASE IF NOT EXISTS hospital_queue_db;
USE hospital_queue_db;

-- Departments table
CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Doctors table
CREATE TABLE doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    doctor_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    dept_id INT NOT NULL,
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
);

-- Patients table
CREATE TABLE patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_name VARCHAR(100) NOT NULL,
    age INT NOT NULL CHECK (age > 0 AND age <= 120),
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Queue tokens/appointments table
CREATE TABLE queue_tokens (
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
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT,
    CHECK (appointment_time > NOW())
);

-- Insert sample data
INSERT INTO departments (dept_name, description) VALUES
('Cardiology', 'Heart and cardiovascular system'),
('Neurology', 'Brain and nervous system'),
('Orthopedics', 'Bones and joints'),
('Pediatrics', 'Children healthcare');

INSERT INTO doctors (doctor_name, specialization, dept_id, phone, email) VALUES
('Dr. John Smith', 'Cardiologist', 1, '1234567890', 'john.smith@hospital.com'),
('Dr. Sarah Johnson', 'Neurologist', 2, '1234567891', 'sarah.johnson@hospital.com'),
('Dr. Mike Wilson', 'Orthopedic Surgeon', 3, '1234567892', 'mike.wilson@hospital.com'),
('Dr. Emily Davis', 'Pediatrician', 4, '1234567893', 'emily.davis@hospital.com');

INSERT INTO patients (patient_name, age, gender, phone, address) VALUES
('Alice Brown', 35, 'Female', '9876543210', '123 Main St'),
('Bob Green', 45, 'Male', '9876543211', '456 Oak Ave'),
('Carol White', 28, 'Female', '9876543212', '789 Pine Rd');

-- Views for reports
CREATE VIEW department_patient_count AS
SELECT 
    d.dept_name,
    COUNT(qt.token_id) as total_patients,
    COUNT(CASE WHEN qt.status = 'Waiting' THEN 1 END) as waiting_patients,
    COUNT(CASE WHEN qt.status = 'Completed' THEN 1 END) as completed_patients
FROM departments d
LEFT JOIN queue_tokens qt ON d.dept_id = qt.dept_id
GROUP BY d.dept_id, d.dept_name;

CREATE VIEW doctor_token_count AS
SELECT 
    d.doctor_name,
    dept.dept_name,
    COUNT(qt.token_id) as total_tokens,
    AVG(CASE WHEN qt.status = 'Completed' THEN 1 ELSE 0 END) * 100 as completion_rate
FROM doctors d
LEFT JOIN queue_tokens qt ON d.doctor_id = qt.doctor_id
LEFT JOIN departments dept ON d.dept_id = dept.dept_id
GROUP BY d.doctor_id, d.doctor_name, dept.dept_name;

CREATE VIEW daily_token_summary AS
SELECT 
    DATE(created_at) as token_date,
    COUNT(*) as tokens_generated,
    COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_tokens,
    COUNT(CASE WHEN status = 'Waiting' THEN 1 END) as pending_tokens
FROM queue_tokens
GROUP BY DATE(created_at)
ORDER BY token_date DESC;

-- Triggers
DELIMITER //

-- Auto-generate token number
CREATE TRIGGER generate_token_number
BEFORE INSERT ON queue_tokens
FOR EACH ROW
BEGIN
    DECLARE dept_code VARCHAR(3);
    DECLARE token_count INT;
    
    SELECT LEFT(dept_name, 3) INTO dept_code 
    FROM departments WHERE dept_id = NEW.dept_id;
    
    SELECT COUNT(*) + 1 INTO token_count 
    FROM queue_tokens 
    WHERE dept_id = NEW.dept_id AND DATE(created_at) = CURDATE();
    
    SET NEW.token_number = CONCAT(UPPER(dept_code), '-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', LPAD(token_count, 3, '0'));
END//

-- Prevent deletion of doctors with active appointments
CREATE TRIGGER prevent_doctor_deletion
BEFORE DELETE ON doctors
FOR EACH ROW
BEGIN
    DECLARE active_count INT;
    SELECT COUNT(*) INTO active_count 
    FROM queue_tokens 
    WHERE doctor_id = OLD.doctor_id AND status IN ('Waiting', 'In Progress');
    
    IF active_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot delete doctor with active appointments';
    END IF;
END//

DELIMITER ;