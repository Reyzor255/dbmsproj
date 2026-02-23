# FRONTEND AND BACKEND ARCHITECTURE

## FRONTEND (Client-Side)

### Technologies Used:
- **HTML5**: Structure and content
- **CSS3**: Styling and layout
- **JavaScript (Vanilla JS)**: Interactivity and AJAX

### Frontend Components:

#### 1. HTML Templates (Views)
Located in: `templates/` folder

**base.html** - Master template with navigation
```html
- Navigation bar with links to all pages
- Common header and footer
- Includes CSS and JS files
```

**index.html** - Dashboard/Home page
```html
- Welcome message
- Quick statistics cards
- Links to main features
```

**departments.html** - Department management
```html
- Add/Edit department form
- Department list table
- Edit and Delete buttons
```

**doctors.html** - Doctor management
```html
- Add/Edit doctor form with department dropdown
- Doctors list table with department names
- Edit and Delete buttons
```

**patients.html** - Patient management
```html
- Add/Edit patient form
- Patients list table
- Edit and Delete buttons
```

**tokens.html** - Token generation and management
```html
- Token generation form (patient, doctor, department, time)
- Tokens list table with status dropdown
- Status update and Delete buttons
```

**reports.html** - Analytics and reports
```html
- Department-wise patient count
- Doctor performance metrics
- Daily token summary
```

#### 2. CSS (Styling)
Located in: `static/css/style.css`

**Key Styles:**
```css
- Gradient navigation bar (purple theme)
- Card-based layout for forms
- Responsive table design
- Button styles (primary, secondary, danger)
- Status-based row colors (waiting, completed, cancelled)
- Form input styling
- Hover effects and transitions
```

#### 3. JavaScript (Interactivity)
Located in: `static/js/main.js` and inline in templates

**Key Functions:**

**Form Handling:**
```javascript
// Show/Hide forms
function showAddForm() { }
function hideForm() { }

// Form submission with AJAX
document.getElementById('form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = { /* form data */ };
    const response = await fetch('/api/endpoint', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const result = await response.json();
    if (result.success) location.reload();
});
```

**CRUD Operations:**
```javascript
// Edit - Populate form with existing data
function editRecord(id, name, ...) {
    document.getElementById('field').value = name;
    isEditing = true;
}

// Delete - Confirm and send DELETE request
async function deleteRecord(id) {
    if (confirm('Are you sure?')) {
        await fetch(`/api/endpoint/${id}`, {method: 'DELETE'});
        location.reload();
    }
}
```

**Auto-fill Department:**
```javascript
// When doctor is selected, auto-fill department
document.getElementById('doctorId').addEventListener('change', function() {
    const deptId = this.options[this.selectedIndex].dataset.dept;
    document.getElementById('deptId').value = deptId;
});
```

---

## BACKEND (Server-Side)

### Technologies Used:
- **Python 3.x**: Programming language
- **Flask**: Web framework
- **MySQL Connector**: Database driver

### Backend Components:

#### 1. Flask Application (app.py)

**Structure:**
```python
from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vroomvroom1!',
    'database': 'hospital_queue_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)
```

#### 2. Routes (URL Endpoints)

**Page Routes (Render HTML):**
```python
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patients')
def patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY patient_id")
    patients = cursor.fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)
```

**API Routes (JSON Response):**

**GET - Retrieve Data:**
```python
@app.route('/api/patients', methods=['GET'])
def api_patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY patient_id")
    patients = cursor.fetchall()
    conn.close()
    return jsonify(patients)
```

**POST - Create Data:**
```python
@app.route('/api/patients', methods=['POST'])
def api_patients():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (patient_name, age, gender, phone, address) 
        VALUES (%s, %s, %s, %s, %s)
    """, (data['patient_name'], data['age'], data['gender'], 
          data['phone'], data['address']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
```

**PUT - Update Data:**
```python
@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def api_patient(patient_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patients SET patient_name=%s, age=%s, gender=%s, phone=%s, address=%s 
        WHERE patient_id=%s
    """, (data['patient_name'], data['age'], data['gender'], 
          data['phone'], data['address'], patient_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
```

**DELETE - Remove Data:**
```python
@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def api_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE patient_id=%s", (patient_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
```

#### 3. Token Generation Logic

```python
@app.route('/api/tokens', methods=['POST'])
def api_tokens():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Validate patient exists
    cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", 
                   (data['patient_id'],))
    if not cursor.fetchone():
        return jsonify({'success': False, 'error': 'Patient not found'}), 400
    
    # Check for duplicate active tokens
    cursor.execute("""
        SELECT token_id FROM queue_tokens 
        WHERE patient_id = %s AND status IN ('Waiting', 'In Progress')
    """, (data['patient_id'],))
    if cursor.fetchone():
        return jsonify({'success': False, 'error': 'Patient already has active token'}), 400
    
    # Generate token number
    cursor.execute("SELECT COUNT(*) as count FROM queue_tokens")
    total_tokens = cursor.fetchone()['count']
    token_number = f"TOK-{datetime.now().strftime('%Y%m%d')}-{(total_tokens + 1):04d}"
    
    # Insert token
    cursor.execute("""
        INSERT INTO queue_tokens (token_number, patient_id, doctor_id, dept_id, 
                                  appointment_time, status) 
        VALUES (%s, %s, %s, %s, %s, 'Waiting')
    """, (token_number, data['patient_id'], data['doctor_id'], 
          data['dept_id'], data['appointment_time']))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'token_number': token_number})
```

#### 4. Reports with SQL Joins

```python
@app.route('/reports')
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Department patient count
    cursor.execute("""
        SELECT d.dept_name, COUNT(qt.token_id) as total_patients,
               COUNT(CASE WHEN qt.status = 'Waiting' THEN 1 END) as waiting_patients,
               COUNT(CASE WHEN qt.status = 'Completed' THEN 1 END) as completed_patients
        FROM departments d
        LEFT JOIN queue_tokens qt ON d.dept_id = qt.dept_id
        GROUP BY d.dept_id, d.dept_name
    """)
    dept_report = cursor.fetchall()
    
    # Doctor token count
    cursor.execute("""
        SELECT d.doctor_name, dept.dept_name, COUNT(qt.token_id) as total_tokens
        FROM doctors d
        LEFT JOIN queue_tokens qt ON d.doctor_id = qt.doctor_id
        LEFT JOIN departments dept ON d.dept_id = dept.dept_id
        GROUP BY d.doctor_id, d.doctor_name, dept.dept_name
    """)
    doctor_report = cursor.fetchall()
    
    conn.close()
    return render_template('reports.html', dept_report=dept_report, 
                         doctor_report=doctor_report)
```

---

## COMMUNICATION FLOW (Frontend ↔ Backend)

### 1. Page Load Flow:
```
User → Browser → Flask Route → Database Query → HTML Template → Browser Display
```

**Example:**
```
1. User visits /patients
2. Flask executes patients() function
3. Queries: SELECT * FROM patients
4. Passes data to patients.html template
5. Template renders with patient data
6. Browser displays the page
```

### 2. AJAX Request Flow:
```
User Action → JavaScript → AJAX Request → Flask API → Database → JSON Response → JavaScript → UI Update
```

**Example (Add Patient):**
```
1. User fills form and clicks "Save"
2. JavaScript captures form data
3. Sends POST request to /api/patients with JSON data
4. Flask receives request, validates data
5. Executes INSERT query
6. Returns JSON: {'success': True}
7. JavaScript receives response
8. Reloads page to show new patient
```

### 3. Data Format:

**Frontend to Backend (Request):**
```javascript
{
    "patient_name": "John Doe",
    "age": 30,
    "gender": "Male",
    "phone": "1234567890",
    "address": "123 Main St"
}
```

**Backend to Frontend (Response):**
```json
{
    "success": true,
    "message": "Patient added successfully"
}
```

---

## KEY CONCEPTS

### 1. RESTful API Design:
- GET: Retrieve data
- POST: Create new data
- PUT: Update existing data
- DELETE: Remove data

### 2. Asynchronous Communication:
- AJAX prevents page reload
- Fetch API returns Promises
- async/await for cleaner code

### 3. Template Rendering:
- Jinja2 template engine
- {{ variable }} for output
- {% for %} for loops
- {% if %} for conditions

### 4. Database Connection:
- Connection pooling
- Cursor for query execution
- dictionary=True for named columns
- Always close connections

### 5. Error Handling:
```python
try:
    # Database operations
    conn.commit()
    return jsonify({'success': True})
except mysql.connector.IntegrityError as e:
    return jsonify({'success': False, 'error': 'Duplicate entry'}), 400
except Exception as e:
    return jsonify({'success': False, 'error': str(e)}), 500
```

---

## FILE STRUCTURE

```
hospital_queue_system/
│
├── app.py                      # Backend (Flask routes and logic)
├── config.py                   # Configuration settings
├── database_schema.sql         # Database structure
├── requirements.txt            # Python dependencies
│
├── templates/                  # Frontend HTML files
│   ├── base.html              # Master template
│   ├── index.html             # Home page
│   ├── departments.html       # Department management
│   ├── doctors.html           # Doctor management
│   ├── patients.html          # Patient management
│   ├── tokens.html            # Token management
│   └── reports.html           # Reports and analytics
│
└── static/                     # Frontend assets
    ├── css/
    │   └── style.css          # Styling
    └── js/
        └── main.js            # JavaScript functions
```

---

## SUMMARY

**FRONTEND:**
- HTML templates for structure
- CSS for styling
- JavaScript for interactivity
- AJAX for dynamic updates

**BACKEND:**
- Flask for routing and logic
- Python for business logic
- MySQL for data storage
- JSON for data exchange

**COMMUNICATION:**
- HTTP methods (GET, POST, PUT, DELETE)
- JSON format for data
- RESTful API design
- Asynchronous requests