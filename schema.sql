-- Smart Student Attendance Management System
-- Regional Maritime University
-- Run this file to set up the database from scratch:
--   mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS attendance_system;
USE attendance_system;

-- Stores all user accounts (students, lecturers, admins)
CREATE TABLE IF NOT EXISTS users (
    user_id       INT          NOT NULL AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL,
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY email (email)
);

-- Student profile linked to a user account
CREATE TABLE IF NOT EXISTS students (
    student_id     INT         NOT NULL AUTO_INCREMENT,
    user_id        INT         DEFAULT NULL,
    student_number VARCHAR(50) NOT NULL,
    programme      VARCHAR(100) DEFAULT NULL,
    year_of_study  INT         DEFAULT NULL,
    PRIMARY KEY (student_id),
    UNIQUE KEY student_number (student_number),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Lecturer profile linked to a user account
CREATE TABLE IF NOT EXISTS lecturers (
    lecturer_id INT         NOT NULL AUTO_INCREMENT,
    user_id     INT         DEFAULT NULL,
    department  VARCHAR(100) DEFAULT NULL,
    staff_id    VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (lecturer_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Courses offered at the institution
CREATE TABLE IF NOT EXISTS courses (
    course_id   INT         NOT NULL AUTO_INCREMENT,
    course_code VARCHAR(20) NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    lecturer_id INT         DEFAULT NULL,
    PRIMARY KEY (course_id),
    UNIQUE KEY course_code (course_code),
    FOREIGN KEY (lecturer_id) REFERENCES lecturers (lecturer_id)
);

-- Links students to the courses they are enrolled in
CREATE TABLE IF NOT EXISTS enrollment (
    enrollment_id INT  NOT NULL AUTO_INCREMENT,
    student_id    INT  DEFAULT NULL,
    course_id     INT  DEFAULT NULL,
    enrolled_date DATE DEFAULT NULL,
    PRIMARY KEY (enrollment_id),
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (course_id)  REFERENCES courses (course_id)
);

-- Class sessions (timetable entries per course)
CREATE TABLE IF NOT EXISTS schedule (
    schedule_id INT          NOT NULL AUTO_INCREMENT,
    course_id   INT          DEFAULT NULL,
    start_time  DATETIME     DEFAULT NULL,
    end_time    DATETIME     DEFAULT NULL,
    venue       VARCHAR(100) DEFAULT NULL,
    day_of_week VARCHAR(20)  DEFAULT NULL,
    PRIMARY KEY (schedule_id),
    FOREIGN KEY (course_id) REFERENCES courses (course_id)
);

-- Attendance records (clock in/out per student per session)
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id    INT      NOT NULL AUTO_INCREMENT,
    student_id       INT      DEFAULT NULL,
    schedule_id      INT      DEFAULT NULL,
    clock_in_time    DATETIME DEFAULT NULL,
    clock_out_time   DATETIME DEFAULT NULL,
    status           VARCHAR(20) DEFAULT NULL,
    duration_minutes FLOAT    DEFAULT NULL,
    PRIMARY KEY (attendance_id),
    FOREIGN KEY (student_id)  REFERENCES students (student_id),
    FOREIGN KEY (schedule_id) REFERENCES schedule (schedule_id)
);

-- Campus geofence location (only one row used)
CREATE TABLE IF NOT EXISTS location (
    location_id   INT          NOT NULL AUTO_INCREMENT,
    venue_name    VARCHAR(100) DEFAULT NULL,
    latitude      FLOAT        DEFAULT NULL,
    longitude     FLOAT        DEFAULT NULL,
    radius_meters FLOAT        DEFAULT NULL,
    PRIMARY KEY (location_id)
);

-- Default campus location (Regional Maritime University, Nungua)
-- Admin can update this from the dashboard after setup
INSERT INTO location (venue_name, latitude, longitude, radius_meters)
VALUES ('Regional Maritime University', 5.6076895, -0.06028, 1000);
