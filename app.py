import socket
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

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f'\n  PC:     http://localhost:5000')
    print(f'  Mobile: http://{local_ip}:5000\n')
    app.run(host='0.0.0.0', port=5000, debug=True)