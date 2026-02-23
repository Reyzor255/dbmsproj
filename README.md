# Hospital Queue Token Management System

A full-stack web application for managing hospital queues, patient appointments, and token generation.

## Features

- **CRUD Operations**: Complete management of Patients, Doctors, Departments, and Queue Tokens
- **SQL JOIN Queries**: Combined information retrieval with patient, doctor, and department details
- **Reports & Analytics**: Aggregate functions and SQL views for comprehensive reporting
- **Database Triggers**: Automatic token generation and data integrity enforcement
- **Data Constraints**: PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, and NOT NULL constraints

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Flask
- **Database**: MySQL

## Database Features

### Tables
- `departments`: Hospital departments with descriptions
- `doctors`: Doctor profiles with specializations and department associations
- `patients`: Patient information with age validation
- `queue_tokens`: Appointment tokens with automatic generation

### Views
- `department_patient_count`: Patient statistics per department
- `doctor_token_count`: Doctor performance metrics
- `daily_token_summary`: Daily token generation reports

### Triggers
- Auto-generate unique token numbers
- Prevent deletion of doctors with active appointments
- Maintain data integrity across operations

### Constraints
- PRIMARY KEY constraints on all tables
- FOREIGN KEY relationships between tables
- UNIQUE constraints for phone numbers and token numbers
- CHECK constraints for age validation and appointment times
- NOT NULL constraints for mandatory fields

## Setup Instructions

### Prerequisites
- Python 3.7+
- MySQL Server 8.0+
- pip (Python package manager)

### Installation

1. **Clone/Download the project**
   ```bash
   cd hospital_queue_system
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup MySQL Database**
   - Start MySQL server
   - Create database and tables:
   ```bash
   mysql -u root -p < database_schema.sql
   ```

4. **Configure Database Connection**
   - Edit `config.py` and update database credentials:
   ```python
   DB_PASSWORD = 'your_mysql_password'
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the Application**
   - Open browser and go to: `http://localhost:5000`

## Usage Guide

### 1. Departments Management
- Add, edit, and delete hospital departments
- View department-wise patient statistics

### 2. Doctors Management
- Register doctors with specializations
- Assign doctors to departments
- Track doctor performance metrics

### 3. Patients Management
- Register patient information
- Validate age and contact details
- Maintain patient records

### 4. Queue Tokens Management
- Generate appointment tokens automatically
- Track token status (Waiting, In Progress, Completed, Cancelled)
- View patient-doctor-department relationships

### 5. Reports & Analytics
- Department-wise patient count
- Doctor performance reports
- Daily token generation summary
- Real-time statistics dashboard

## Key SQL Features Implemented

### JOIN Queries
```sql
-- Patient, Doctor, Department information
SELECT qt.*, p.patient_name, d.doctor_name, dept.dept_name
FROM queue_tokens qt
JOIN patients p ON qt.patient_id = p.patient_id
JOIN doctors d ON qt.doctor_id = d.doctor_id
JOIN departments dept ON qt.dept_id = dept.dept_id
```

### Aggregate Functions
```sql
-- Department patient count with status breakdown
SELECT 
    d.dept_name,
    COUNT(qt.token_id) as total_patients,
    COUNT(CASE WHEN qt.status = 'Waiting' THEN 1 END) as waiting_patients
FROM departments d
LEFT JOIN queue_tokens qt ON d.dept_id = qt.dept_id
GROUP BY d.dept_id, d.dept_name
```

### Triggers
```sql
-- Auto-generate token numbers
CREATE TRIGGER generate_token_number
BEFORE INSERT ON queue_tokens
FOR EACH ROW
BEGIN
    -- Generate unique token: DEPT-YYYYMMDD-001
    SET NEW.token_number = CONCAT(dept_code, '-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', token_count);
END
```

## File Structure

```
hospital_queue_system/
├── app.py                 # Flask application
├── config.py             # Configuration settings
├── database_schema.sql   # Database schema with triggers
├── requirements.txt      # Python dependencies
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── departments.html
│   ├── doctors.html
│   ├── patients.html
│   ├── tokens.html
│   └── reports.html
└── static/             # CSS and JavaScript
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## API Endpoints

- `GET/POST /api/departments` - Department CRUD
- `GET/POST /api/doctors` - Doctor CRUD  
- `GET/POST /api/patients` - Patient CRUD
- `GET/POST /api/tokens` - Token CRUD
- `PUT/DELETE /api/{resource}/{id}` - Update/Delete operations

## Security Features

- Input validation and sanitization
- SQL injection prevention using parameterized queries
- Data integrity constraints
- Error handling and user feedback

## Future Enhancements

- User authentication and role-based access
- SMS/Email notifications for appointments
- Real-time queue status updates
- Mobile-responsive design improvements
- Advanced reporting with charts and graphs