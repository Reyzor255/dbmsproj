-- Add users table for authentication
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'doctor', 'receptionist') NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default users
INSERT INTO users (username, password, full_name, role, email) VALUES
('admin', 'admin123', 'System Administrator', 'admin', 'admin@hospital.com'),
('doctor1', 'doctor123', 'Dr. John Smith', 'doctor', 'john.smith@hospital.com'),
('reception', 'reception123', 'Reception Desk', 'receptionist', 'reception@hospital.com');
