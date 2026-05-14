from flask import Blueprint, request, jsonify, render_template
from database import get_db
import bcrypt
import jwt
import datetime

auth =Blueprint('auth', __name__)

SECRET_KEY ="attendance_secret_key"

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']
    role = data['role']
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db = get_db()
    cursor = db.cursor()
    
    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        return jsonify({"message": "Email already exists"}), 400
    
    cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                   (name, email, password_hash, role))
    db.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        token = jwt.encode({
            'user_id': user[0],
            'role': user[4],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY)
        return jsonify({'token': token, 'role': user[4], 'user_id': user[0]}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@auth.route('/login')
def login_page():
    return render_template('login.html')

@auth.route('/register')
def register_page():
    return render_template('register.html')

@auth.route('/student-dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@auth.route('/lecturer-dashboard')
def lecturer_dashboard():
    return render_template('lecturer_dashboard.html')

@auth.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')