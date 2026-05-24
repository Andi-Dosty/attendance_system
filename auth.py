from flask import Blueprint, request, jsonify, render_template
from database import get_db
import bcrypt
import jwt
import datetime
import os

auth = Blueprint('auth', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'attendance_secret_key')
LECTURER_CODE = os.environ.get('LECTURER_CODE', 'RMU-LECT-2026')
ADMIN_CODE = os.environ.get('ADMIN_CODE', 'RMU-ADMIN-2026')


def create_user(name, email, password, role):
    if not name or not email or not password:
        return None, "Name, email and password are required"
    if '@' not in email:
        return None, "Invalid email address"
    if len(password) < 6:
        return None, "Password must be at least 6 characters"
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return None, "An account with this email already exists"

        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                       (name, email, password_hash, role))
        db.commit()
        user_id = cursor.lastrowid

        if role == 'student':
            student_number = f'STU{user_id:04d}'
            cursor.execute("INSERT INTO students (user_id, student_number, programme, year_of_study) VALUES (%s, %s, %s, %s)",
                           (user_id, student_number, 'General', 1))
            db.commit()

        if role == 'lecturer':
            staff_id = f'STAFF{user_id:04d}'
            cursor.execute("INSERT INTO lecturers (user_id, department, staff_id) VALUES (%s, %s, %s)",
                           (user_id, 'General', staff_id))
            db.commit()

        return user_id, None
    except Exception as ex:
        return None, f"Registration failed: {str(ex)}"


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400
    _, error = create_user(data.get('name', ''), data.get('email', ''), data.get('password', ''), 'student')
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Student registered successfully"}), 201


@auth.route('/lecturer-register', methods=['POST'])
def lecturer_register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400
    if not data.get('lecturer_code'):
        return jsonify({"message": "Lecturer code is required"}), 400
    if data.get('lecturer_code') != LECTURER_CODE:
        return jsonify({"message": "Invalid lecturer code"}), 403
    _, error = create_user(data.get('name', ''), data.get('email', ''), data.get('password', ''), 'lecturer')
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Lecturer registered successfully"}), 201


@auth.route('/admin-register', methods=['POST'])
def admin_register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400
    if not data.get('admin_code'):
        return jsonify({"message": "Admin code is required"}), 400
    if data.get('admin_code') != ADMIN_CODE:
        return jsonify({"message": "Invalid admin code"}), 403
    _, error = create_user(data.get('name', ''), data.get('email', ''), data.get('password', ''), 'admin')
    if error:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Admin registered successfully"}), 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user[3].encode('utf-8')):
        token = jwt.encode({
            'user_id': user[0],
            'role': user[4],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, SECRET_KEY)
        return jsonify({'token': token, 'role': user[4], 'user_id': user[0]}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


@auth.route('/login')
def login_page():
    return render_template('login.html')

@auth.route('/register')
def register_page():
    return render_template('register.html')

@auth.route('/lecturer-register')
def lecturer_register_page():
    return render_template('lecturer_register.html')

@auth.route('/admin-register')
def admin_register_page():
    return render_template('admin_register.html')

@auth.route('/student-dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@auth.route('/lecturer-dashboard')
def lecturer_dashboard():
    return render_template('lecturer_dashboard.html')

@auth.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@auth.route('/courses')
def courses_page():
    return render_template('courses.html')

@auth.route('/schedule-management')
def schedule_management():
    return render_template('schedule.html')

@auth.route('/enrollment')
def enrollment_page():
    return render_template('enrollment.html')

@auth.route('/reports')
def reports_page():
    return render_template('reports.html')
