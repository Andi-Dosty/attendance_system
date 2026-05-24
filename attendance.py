from flask import Blueprint, request, jsonify, render_template, Response
from database import get_db
import math
import datetime
import jwt
import os
import csv
import io

attendance = Blueprint('attendance', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'attendance_secret_key')

def verify_token(request):
    token = request.headers.get('Authorization')
    if not token:
        return None
    try:
        token = token.split(' ')[1]
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
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
    cursor = db.cursor(buffered=True)
    cursor.execute("SELECT * FROM location LIMIT 1")
    location = cursor.fetchone()

    if not location:
        return jsonify({'message': 'Campus location not set'}), 400

    campus_lat = location[2]
    campus_lng = location[3]
    radius = location[4]

    if not check_geofence(student_lat, student_lng, campus_lat, campus_lng, radius):
        return jsonify({'message': 'You are outside the campus boundary'}), 403

    cursor.execute("SELECT student_id FROM students WHERE user_id = %s", (student_id,))
    student = cursor.fetchone()
    if not student:
        return jsonify({'message': 'Student not found'}), 404
    actual_student_id = student[0]
    
    clock_in_time = datetime.datetime.now()
    cursor.execute("SELECT start_time FROM schedule WHERE schedule_id = %s", (schedule_id,))
    session = cursor.fetchone()

    status = 'present'
    if session:
        session_start = session[0]
        # MySQL TIME columns return as timedelta; convert to datetime for comparison
        if isinstance(session_start, datetime.timedelta):
            session_start = datetime.datetime.combine(clock_in_time.date(),
                                (datetime.datetime.min + session_start).time())
        if clock_in_time > session_start:
            status = 'late'

    cursor.execute("INSERT INTO attendance (student_id, schedule_id, clock_in_time, status) VALUES (%s, %s, %s, %s)",
                   (actual_student_id, schedule_id, clock_in_time, status))
    db.commit()
    attendance_id = cursor.lastrowid

    return jsonify({'message': 'Clocked in successfully', 'clock_in_time': str(clock_in_time), 'attendance_id': attendance_id}), 201

@attendance.route('/clock-out', methods=['POST'])
def clock_out():
    user = verify_token(request)
    if not user:
        return jsonify({'message': 'Unauthorized. Please login first.'}), 401
    data = request.get_json()
    attendance_id = data['attendance_id']

    clock_out_time = datetime.datetime.now()

    db = get_db()
    cursor = db.cursor(buffered=True)
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
    cursor = db.cursor(buffered=True)

    if user['role'] == 'student':
        cursor.execute("SELECT student_id FROM students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return jsonify([]), 200
        cursor.execute("""
            SELECT a.attendance_id, a.student_id, a.schedule_id, a.clock_in_time,
                   a.clock_out_time, a.status, a.duration_minutes, c.course_name
            FROM attendance a
            LEFT JOIN schedule s ON a.schedule_id = s.schedule_id
            LEFT JOIN courses c ON s.course_id = c.course_id
            WHERE a.student_id = %s
            ORDER BY a.clock_in_time DESC
        """, (student[0],))
    else:
        cursor.execute("""
            SELECT a.attendance_id, a.student_id, a.schedule_id, a.clock_in_time,
                   a.clock_out_time, a.status, a.duration_minutes, c.course_name
            FROM attendance a
            LEFT JOIN schedule s ON a.schedule_id = s.schedule_id
            LEFT JOIN courses c ON s.course_id = c.course_id
            ORDER BY a.clock_in_time DESC
        """)

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
            'duration_minutes': record[6],
            'course_name': record[7] if record[7] else 'N/A'
        })

    return jsonify(result), 200

@attendance.route('/admin-stats', methods=['GET'])
def admin_stats():
    user = verify_token(request)
    if not user or user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized. Admin access required.'}), 401
    db = get_db()
    cursor = db.cursor(buffered=True)
    
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
    cursor = db.cursor(buffered=True)
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
    cursor = db.cursor(buffered=True)
    cursor.execute("UPDATE location SET venue_name=%s, latitude=%s, longitude=%s, radius_meters=%s WHERE location_id=1",
                   (data['venue_name'], data['latitude'], data['longitude'], data['radius_meters']))
    db.commit()
    return jsonify({'message': 'Location updated successfully'}), 200


@attendance.route('/schedules', methods=['GET'])
def get_schedules():
    user = verify_token(request)
    if not user:
        return jsonify({'message': 'Unauthorized. Please login first.'}), 401

    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("""
        SELECT s.schedule_id, s.start_time, s.end_time, s.venue, s.day_of_week, c.course_name
        FROM schedule s
        JOIN courses c ON s.course_id = c.course_id
    """)
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            'schedule_id': row[0],
            'start_time': str(row[1]),
            'end_time': str(row[2]),
            'venue': row[3],
            'day_of_week': row[4],
            'course_name': row[5]
        })

    return jsonify(result), 200


@attendance.route('/api/reports', methods=['GET'])
def reports():
    user = verify_token(request)
    if not user or user['role'] not in ['admin', 'lecturer']:
        return jsonify({'message': 'Unauthorized.'}), 401

    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT status, COUNT(*) FROM attendance GROUP BY status")
    status_rows = cursor.fetchall()
    status_data = {row[0]: row[1] for row in status_rows}

    cursor.execute("""
        SELECT c.course_name, COUNT(a.attendance_id)
        FROM attendance a
        JOIN schedule s ON a.schedule_id = s.schedule_id
        JOIN courses c ON s.course_id = c.course_id
        GROUP BY c.course_name
    """)
    course_rows = cursor.fetchall()

    cursor.execute("""
        SELECT u.name, c.course_name, a.clock_in_time, a.status, a.duration_minutes
        FROM attendance a
        JOIN students st ON a.student_id = st.student_id
        JOIN users u ON st.user_id = u.user_id
        JOIN schedule s ON a.schedule_id = s.schedule_id
        JOIN courses c ON s.course_id = c.course_id
        ORDER BY a.clock_in_time DESC
        LIMIT 20
    """)
    recent_rows = cursor.fetchall()

    return jsonify({
        'status_breakdown': status_data,
        'attendance_by_course': [{'course': r[0], 'count': r[1]} for r in course_rows],
        'recent_records': [{
            'student_name': r[0],
            'course_name': r[1],
            'clock_in_time': str(r[2]) if r[2] else '-',
            'status': r[3],
            'duration_minutes': round(r[4]) if r[4] else '-'
        } for r in recent_rows]
    }), 200


@attendance.route('/api/export-csv', methods=['GET'])
def export_csv():
    user = verify_token(request)
    if not user or user['role'] not in ['admin', 'lecturer']:
        return jsonify({'message': 'Unauthorized.'}), 401

    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("""
        SELECT u.name, c.course_name, a.clock_in_time, a.clock_out_time,
               a.status, a.duration_minutes
        FROM attendance a
        JOIN students st ON a.student_id = st.student_id
        JOIN users u ON st.user_id = u.user_id
        JOIN schedule s ON a.schedule_id = s.schedule_id
        JOIN courses c ON s.course_id = c.course_id
        ORDER BY a.clock_in_time DESC
    """)
    rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student Name', 'Course', 'Clock In', 'Clock Out', 'Status', 'Duration (mins)'])
    for row in rows:
        writer.writerow([
            row[0], row[1],
            str(row[2]) if row[2] else '-',
            str(row[3]) if row[3] else '-',
            row[4],
            round(row[5]) if row[5] else '-'
        ])

    output.seek(0)
    filename = f"attendance_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@attendance.route('/api/enroll', methods=['POST'])
def enroll():
    user = verify_token(request)
    if not user or user['role'] != 'student':
        return jsonify({'message': 'Unauthorized. Students only.'}), 401

    data = request.get_json()
    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT student_id FROM students WHERE user_id = %s", (user['user_id'],))
    student = cursor.fetchone()
    if not student:
        return jsonify({'message': 'Student not found'}), 404
    student_id = student[0]

    cursor.execute("SELECT * FROM enrollment WHERE student_id = %s AND course_id = %s", (student_id, data['course_id']))
    if cursor.fetchone():
        return jsonify({'message': 'Already enrolled in this course'}), 400

    cursor.execute("INSERT INTO enrollment (student_id, course_id, enrolled_date) VALUES (%s, %s, CURDATE())",
                   (student_id, data['course_id']))
    db.commit()
    return jsonify({'message': 'Enrolled successfully'}), 201


@attendance.route('/api/my-courses', methods=['GET'])
def my_courses():
    user = verify_token(request)
    if not user or user['role'] != 'student':
        return jsonify({'message': 'Unauthorized. Students only.'}), 401

    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT student_id FROM students WHERE user_id = %s", (user['user_id'],))
    student = cursor.fetchone()
    if not student:
        return jsonify([]), 200

    cursor.execute("""
        SELECT c.course_id, c.course_code, c.course_name, e.enrolled_date
        FROM enrollment e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = %s
    """, (student[0],))
    rows = cursor.fetchall()

    return jsonify([{
        'course_id': r[0],
        'course_code': r[1],
        'course_name': r[2],
        'enrolled_date': str(r[3])
    } for r in rows]), 200


@attendance.route('/api/schedules', methods=['POST'])
def add_schedule():
    user = verify_token(request)
    if not user or user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized. Admin access required.'}), 401

    data = request.get_json()
    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT course_id FROM courses WHERE course_id = %s", (data['course_id'],))
    if not cursor.fetchone():
        return jsonify({'message': 'Course not found'}), 404

    cursor.execute("""
        INSERT INTO schedule (course_id, start_time, end_time, venue, day_of_week)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['course_id'], data['start_time'], data['end_time'], data['venue'], data['day_of_week']))
    db.commit()

    return jsonify({'message': 'Schedule added successfully'}), 201


@attendance.route('/api/courses', methods=['GET'])
def get_courses():
    user = verify_token(request)
    if not user:
        return jsonify({'message': 'Unauthorized. Please login first.'}), 401

    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    result = []
    for course in courses:
        result.append({
            'course_id': course[0],
            'course_code': course[1],
            'course_name': course[2],
            'lecturer_id': course[3]
        })

    return jsonify(result), 200

@attendance.route('/api/courses', methods=['POST'])
def add_course():
    user = verify_token(request)
    if not user or user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized. Admin access required.'}), 401

    data = request.get_json()
    db = get_db()
    cursor = db.cursor(buffered=True)
    
    cursor.execute("SELECT lecturer_id FROM lecturers WHERE user_id = %s", (data['lecturer_id'],))
    lecturer = cursor.fetchone()
    if not lecturer:
        return jsonify({'message': 'Lecturer not found'}), 404

    cursor.execute("INSERT INTO courses (course_code, course_name, lecturer_id) VALUES (%s, %s, %s)",
                   (data['course_code'], data['course_name'], lecturer[0]))
    db.commit()

    return jsonify({'message': 'Course added successfully'}), 201
