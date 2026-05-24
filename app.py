from flask import Flask
from dotenv import load_dotenv
load_dotenv()

from auth import auth
from attendance import attendance

app = Flask(__name__)

app.register_blueprint(auth)
app.register_blueprint(attendance)

@app.route('/')
def home():
    return 'Attendance System is running!'

@app.errorhandler(404)
def not_found(_e):
    return {'message': 'Resource not found'}, 404

@app.errorhandler(500)
def server_error(_e):
    return {'message': 'An internal server error occurred. Please try again.'}, 500

@app.errorhandler(405)
def method_not_allowed(_e):
    return {'message': 'Method not allowed'}, 405

if __name__ == '__main__':
    app.run(debug=True)