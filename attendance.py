from flask import Blueprint, request, jsonify, render_template
from database import get_db
import math
import datetime
import jwt 

attendance = Blueprint('attendance', __name__)

def verify_token(request):
    token = request.headers.get('Authorization')
    if not token:
        return None
    try:
        token = token.split(' ')[1]
        data = jwt.decode(token, 'attendance_secret_key', algorithms=['HS256'])
        return data
    except:
        return None

def check_geofence(student_lat, student_lng, campus_lat, campus_lng, radius_meters):
    R = 6371000
    lat1 = math.radians(student_lat)
    lat2 = math.radians(campus_lat)
    dlat = math.radians(campus_lat - student_lat)
    dlng = math.radians(campus_lng - student_lng)

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return distance <= radius_meters

@attendance.route('/clock-in', methods=['POST'])
def clock_in():
    user = verify_token(request)
    if not user:
        return jsonify({'message': 'Unauthorized. Please login first.'}), 401
    data = request.get_json()
    student_id = data['student_id']
    schedule_id = data['schedule_id']
    student_lat = data['latitude']
    student_lng = data['longitude']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM location LIMIT 1")
    location = cursor.fetchone()

    if not location:
        return jsonify({'message': 'Campus location not set'}), 400

    campus_lat = location[2]
    campus_lng = location[3]
    radius = location[4]

    if not check_geofence(student_lat, student_lng, campus_lat, campus_lng, radius):
        return jsonify({'message': 'You are outside the campus boundary'}), 403

    clock_in_time = datetime.datetime.now()
    cursor.execute("INSERT INTO attendance (student_id, schedule_id, clock_in_time, status) VALUES (%s, %s, %s, %s)",
                   (student_id, schedule_id, clock_in_time, 'present'))
    db.commit()

    return jsonify({'message': 'Clocked in successfully', 'clock_in_time': str(clock_in_time)}), 201

@attendance.route('/clock-out', methods=['POST'])
def clock_out():
    user = verify_token(request)
    if not user:
        return jsonify({'message': 'Unauthorized. Please login first.'}), 401
    data = request.get_json()
    attendance_id = data['attendance_id']

    clock_out_time = datetime.datetime.now()

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT clock_in_time FROM attendance WHERE attendance_id = %s", (attendance_id,))
    record = cursor.fetchone()

    if not record:
        return jsonify({'message': 'Attendance record not found'}), 404

    clock_in_time = record[0]
    duration = (clock_out_time - clock_in_time).total_seconds() / 60

    cursor.execute("UPDATE attendance SET clock_out_time = %s, duration_minutes = %s WHERE attendance_id = %s",
                   (clock_out_time, duration, attendance_id))
    db.commit()

    return jsonify({'message': 'Clocked out successfully', 'duration_minutes': duration}), 200

@attendance.route('/attendance-records', methods=['GET'])
def attendance_records():
    user = verify_token(request)
    if not user:
        return jsonify({'message': 'Unauthorized. Please login first.'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM attendance")
    records = cursor.fetchall()

    result = []
    for record in records:
        result.append({
            'attendance_id': record[0],
            'student_id': record[1],
            'schedule_id': record[2],
            'clock_in_time': str(record[3]) if record[3] else None,
            'clock_out_time': str(record[4]) if record[4] else None,
            'status': record[5],
            'duration_minutes': record[6]
        })

    return jsonify(result), 200

@attendance.route('/admin-stats', methods=['GET'])
def admin_stats():
    user = verify_token(request)
    if not user or user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized. Admin access required.'}), 401
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]
    
    return jsonify({
        'total_users': total_users,
        'total_attendance': total_attendance,
        'total_courses': total_courses
    }), 200

@attendance.route('/admin-users', methods=['GET'])
def admin_users():
    user = verify_token(request)
    if not user or user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized. Admin access required.'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    result = []
    for user in users:
        result.append({
            'user_id': user[0],
            'name': user[1],
            'email': user[2],
            'role': user[4],
            'created_at': str(user[5])
        })

    return jsonify(result), 200

@attendance.route('/update-location', methods=['POST'])
def update_location():
    user = verify_token(request)
    if not user or user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized. Admin access required.'}), 401
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE location SET venue_name=%s, latitude=%s, longitude=%s, radius_meters=%s WHERE location_id=1",
                   (data['venue_name'], data['latitude'], data['longitude'], data['radius_meters']))
    db.commit()
    return jsonify({'message': 'Location updated successfully'}), 200

