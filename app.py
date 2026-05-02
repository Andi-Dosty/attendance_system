from flask import Flask
from auth import auth
from attendance import attendance

app = Flask(__name__)

app.register_blueprint(auth)
app.register_blueprint(attendance)

@app.route('/')
def home():
    return 'Attendance System is running!'

if __name__ == '__main__':
    app.run(debug=True)