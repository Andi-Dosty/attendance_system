# Smart Student Attendance Management System
Regional Maritime University

A web-based attendance system with geofencing, role-based access control, and real-time reporting.

---

## Features

- Students clock in/out with GPS location verification (must be on campus)
- Late detection based on scheduled session start time
- Lecturer and admin dashboards with attendance reports and CSV export
- Course and schedule management
- Secure registration with role codes (lecturer and admin)

---

## Tech Stack

- **Backend:** Python / Flask
- **Database:** MySQL
- **Auth:** JWT tokens + bcrypt password hashing
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Charts:** Chart.js (CDN)

---

## Setup Instructions

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up the database

Run the schema file to create all tables:

```bash
mysql -u root -p < schema.sql
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env`:

```
SECRET_KEY=your_secret_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=attendance_system
LECTURER_CODE=RMU-LECT-2026
ADMIN_CODE=RMU-ADMIN-2026
```

### 4. Run the app

```bash
python app.py
```

The server starts at `http://localhost:5000` (or `http://172.20.10.4:5000` from other devices on the same network)

---

## User Roles

| Role | Registration | Default Redirect |
|------|-------------|-----------------|
| Student | `/register` | `/student-dashboard` |
| Lecturer | `/lecturer-register` (requires code) | `/lecturer-dashboard` |
| Admin | `/admin-register` (requires code) | `/admin-dashboard` |

> Lecturer and admin registration codes are set in the `.env` file.

---

## Pages

**On this PC:** `http://localhost:5000`  
**On other devices (same network):** `http://172.20.10.4:5000`

| URL | PC | Phone / Other Device | Access |
|-----|----|----------------------|--------|
| /login | [localhost:5000/login](http://localhost:5000/login) | [172.20.10.4:5000/login](http://172.20.10.4:5000/login) | All |
| /register | [localhost:5000/register](http://localhost:5000/register) | [172.20.10.4:5000/register](http://172.20.10.4:5000/register) | Public |
| /lecturer-register | [localhost:5000/lecturer-register](http://localhost:5000/lecturer-register) | [172.20.10.4:5000/lecturer-register](http://172.20.10.4:5000/lecturer-register) | Code required |
| /admin-register | [localhost:5000/admin-register](http://localhost:5000/admin-register) | [172.20.10.4:5000/admin-register](http://172.20.10.4:5000/admin-register) | Code required |
| /student-dashboard | [localhost:5000/student-dashboard](http://localhost:5000/student-dashboard) | [172.20.10.4:5000/student-dashboard](http://172.20.10.4:5000/student-dashboard) | Student |
| /enrollment | [localhost:5000/enrollment](http://localhost:5000/enrollment) | [172.20.10.4:5000/enrollment](http://172.20.10.4:5000/enrollment) | Student |
| /lecturer-dashboard | [localhost:5000/lecturer-dashboard](http://localhost:5000/lecturer-dashboard) | [172.20.10.4:5000/lecturer-dashboard](http://172.20.10.4:5000/lecturer-dashboard) | Lecturer |
| /admin-dashboard | [localhost:5000/admin-dashboard](http://localhost:5000/admin-dashboard) | [172.20.10.4:5000/admin-dashboard](http://172.20.10.4:5000/admin-dashboard) | Admin |
| /courses | [localhost:5000/courses](http://localhost:5000/courses) | [172.20.10.4:5000/courses](http://172.20.10.4:5000/courses) | Admin |
| /schedule-management | [localhost:5000/schedule-management](http://localhost:5000/schedule-management) | [172.20.10.4:5000/schedule-management](http://172.20.10.4:5000/schedule-management) | Admin |
| /reports | [localhost:5000/reports](http://localhost:5000/reports) | [172.20.10.4:5000/reports](http://172.20.10.4:5000/reports) | Admin / Lecturer |

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `users` | All accounts (students, lecturers, admins) |
| `students` | Student profiles linked to users |
| `lecturers` | Lecturer profiles linked to users |
| `courses` | Course catalogue |
| `enrollment` | Student-course relationships |
| `schedule` | Class sessions (timetable) |
| `attendance` | Clock-in/out records |
| `location` | Campus geofence coordinates |

---

## Security Notes

- Never commit `.env` to GitHub — it contains your database password and secret keys
- The `.env.example` file is safe to commit (it has no real values)
- JWT tokens expire after 24 hours
- Clock-in is tied to the logged-in user's token — students cannot mark attendance for others
- Geofence default: Regional Maritime University, Nungua (lat: 5.6076895, lng: -0.06028, radius: 1000m)

---

## Project Team

- Shelter Deladem Ziwu - BIT000825
- Andy Sackey - BCS0000327
- Obed-Ackah Armah - BIT0004226

Regional Maritime University
