import mysql.connector

def get_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Familyiskey0",
        database="attendance_system"
    )
    return db