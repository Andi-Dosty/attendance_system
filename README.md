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

The server starts at `http://localhost:5000`

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

| URL | Description | Access |
|-----|-------------|--------|
| `/login` | Login page | All |
| `/register` | Student registration | Public |
| `/lecturer-register` | Lecturer registration | Code required |
| `/admin-register` | Admin registration | Code required |
| `/student-dashboard` | Clock in/out + attendance history | Student |
| `/enrollment` | Browse and enroll in courses | Student |
| `/lecturer-dashboard` | View attendance records | Lecturer |
| `/admin-dashboard` | Manage users, geofence | Admin |
| `/courses` | Add and manage courses | Admin |
| `/schedule-management` | Add and manage class sessions | Admin |
| `/reports` | Charts, stats, CSV export | Admin / Lecturer |

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
