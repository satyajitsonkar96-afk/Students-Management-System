# 🎓 Student Management System | Role-Based Flask App on AWS

> A production-ready, cloud-native web application for managing student records with secure role-based access (Admin / Teacher). Built with Flask, MySQL (AWS RDS), and deployed on AWS EC2 behind Nginx + Gunicorn.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-black)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20RDS-orange)
![MySQL](https://img.shields.io/badge/MySQL-AWS%20RDS-blue)
![Deployed](https://img.shields.io/badge/deployed-live-success)

---

## 🔍 Why This Project?

Educational institutions struggle with scattered student data, manual errors, and lack of access control.  
This system solves that by providing:

- **Centralized digital records**  
- **Role-based security** (Admin: full control | Teacher: view/search only)  
- **Cloud deployment** for 24/7 availability  
- **Scalable architecture** ready for 1000+ users  

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | Secure login with password hashing (werkzeug) |
| 👥 **Role-based Access** | Admin (CRUD) & Teacher (read-only) |
| 📝 **Student Management** | Add, edit, delete, view all records |
| 🔍 **Instant Search** | Search by name, email, or course |
| ☁️ **Cloud Native** | AWS EC2 + RDS (MySQL) |
| 🚀 **High Performance** | Gunicorn (WSGI) + Nginx (reverse proxy) |
| 🔒 **Security** | Environment variables, RDS security groups, HTTPS ready |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Flask, Gunicorn |
| Frontend | HTML5, CSS3, Jinja2 |
| Database | MySQL (AWS RDS) |
| Server | AWS EC2 (Ubuntu 22.04), Nginx |
| Auth | Session-based, password hashing |
| Deployment | Git, pip, systemd |

---

## 🏗 Architecture Overview

User → Nginx (80/443) → Gunicorn (8000) → Flask App → AWS RDS (MySQL)  
↑  
Admin/Teacher  

- **Nginx** serves static files & reverse proxies dynamic requests.  
- **Gunicorn** manages multiple Flask worker processes.  
- **RDS** provides managed, auto-backup, scalable database.  

---

## 📁 Project Structure (Clean MVC)

```
Student_management/
student-management-system/
│
├── app.py
├── config.py
├── requirements.txt
├── Dump20260327.sql
│
├── models/
│   ├── db.py
│   └── student.py
│
├── routes/
│   ├── admin_routes.py
│   ├── main_routes.py
│   └── student_routes.py
│
├── templates/
│   ├── admin_add.html
│   ├── admin_dashboard.html
│   ├── admin_edit.html
│   ├── admin_login.html
│   ├── login.html
│   └── index.html
│
├── utils/
│   └── helpers.py
│
├── static/
│
├── .gitignore
└── README.md    
```

---

## ⚙️ Local Setup (for testing)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/student-management-system.git
cd student-management-system

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (create .env)
DB_HOST=your-rds-endpoint
DB_USER=admin
DB_PASSWORD=your-pw
DB_NAME=student_db
SECRET_KEY=your-secret

# 5. Run locally
python app.py
```




## 🗄️ Database Setup (AWS RDS)

### 1️⃣ Create an RDS MySQL Instance

* Go to **AWS Console → RDS → Create Database**
* Select:

  * Engine: **MySQL**
  * Template: **Free Tier (db.t3.micro)**
* Set:

  * **Master Username**
  * **Master Password** *(store securely)*

#### Configuration:

* **Public Accessibility:** ❌ No (for security)
* **VPC:** Same as your EC2 instance *(or ensure VPC peering)*
* **Security Group:** Allow MySQL access from EC2

---

### 2️⃣ Configure Security Group

1. Go to **EC2 Dashboard**

2. Note the **Security Group** attached to your EC2 instance

3. Go to **RDS → Security Groups**

4. Add an **Inbound Rule**:

| Type         | Port | Source                           |
| ------------ | ---- | -------------------------------- |
| MySQL/Aurora | 3306 | EC2 Security Group (recommended) |

---

### 3️⃣ Connect to RDS from EC2

Run the following command on your EC2 instance:

```bash
mysql -h <your-rds-endpoint> -u <username> -p
```

---

### 4️⃣ Create Database

```sql
CREATE DATABASE student_db;
USE student_db;
```

---

### 5️⃣ Create Tables

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher') DEFAULT 'teacher'
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    course VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 6️⃣ Insert Default Admin User

```sql
-- Replace with a properly hashed password from your application
INSERT INTO users (username, password, role)
VALUES ('admin', 'scrypt:32768:8:1$...', 'admin');
```


## ☁️ AWS Deployment (Production)

| Service | Purpose |
|--------|--------|
| EC2 (t2.micro) | Hosts Nginx, Gunicorn, Flask app |
| RDS (db.t3.micro) | MySQL database |
| Security Groups | Ports: 22, 80, 443, 3306 |
| Gunicorn | `gunicorn --workers 3 --bind 127.0.0.1:8000 app:app` |
| Nginx | Reverse proxy |
| systemd | Auto-restart Gunicorn |

### Deployment Steps

1. Launch EC2 (Ubuntu), install Python, pip, nginx  
2. Clone repo, setup venv, install requirements  
3. Configure RDS security group  
4. Set environment variables  
5. Run Gunicorn as systemd service  
6. Configure Nginx reverse proxy  

---

## 🔐 Security Highlights

- Password hashing with `werkzeug.security`
- No hardcoded secrets
- RDS private access only
- Secure session handling
- SQL injection prevention (parameterized queries)

---

## 📈 Performance & Scalability

- Gunicorn multi-workers  
- Nginx static file serving  
- MySQL optimization ready  
- Future Redis caching support  

---


-## 🚀 Future Updates

- 📚 **Academic Records & Results**
  - Add complete student academic history (semester-wise subjects, marks, GPA)
  - Generate automated results and performance analytics
  - Enable downloadable report cards (PDF)

- 👥 **Admin User Management**
  - Admin can create, update, and delete teacher accounts
  - Role management (Admin ↔ Teacher)
  - Account activation and suspension system
  - Maintain audit logs for admin actions

- 📧 **Email Notifications**
  - Send emails for student registration, result updates, and account creation
  - Integrate with SMTP or AWS SES
  - Optional OTP-based authentication

- 🐳 **Dockerization**
  - Containerize Flask application and database
  - Use Docker Compose for multi-container setup
  - Ensure consistent development and production environments

- 🔁 **CI/CD Pipeline**
  - Implement GitHub Actions for automation
  - Automate build, test, and deployment workflow
  - Deploy updates to AWS EC2 with minimal downtime 

---

## 👨‍💻 Author

**Yash Sonkar**  
BSc Cloud Computing Student  

📧 satyajitsonkar96@gmail.com	 

