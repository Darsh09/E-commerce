from flask import Flask, request, jsonify, session
import psycopg2
from dotenv import load_dotenv
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from datetime import timedelta

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv('DBNAME'),
    user=os.getenv('USER'),
    password=os.getenv('PASSWORD'),
    host=os.getenv('HOST'),
    port=os.getenv('PORT')
)

cursor = conn.cursor()

app = Flask(__name__)

# Limiter configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Configure Flask session
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set this in your .env
app.config['SESSION_TYPE'] = 'filesystem'  # Session will be stored on the filesystem
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Session valid for 1 day

# Initialize Flask-Session
Session(app)

@app.route("/register", methods=['POST'])
# @limiter.limit("100 per minute")
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    email = data.get('email')
    password = data.get('password')

    cursor.execute("SELECT 1 FROM users WHERE email = %s;", (email,))

    user = cursor.fetchone()

    if user:
        return jsonify({'message': 'User Already Exists'}), 409
    else:
        cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s);', (email, password))
        conn.commit()
        return jsonify({'message': 'User created'}), 200

@app.route("/login", methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    cursor.execute("SELECT 1 FROM users WHERE email = %s AND password = %s;", (email, password))

    user = cursor.fetchone()

    if user:
        session['email'] = email
        session.permanent = True
        
        return jsonify({"message": "User logged in", "session": "Session started"}), 200
    else:
        return jsonify({"message": "Incorrect email or password"}), 404

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('email', None)
    return jsonify({"message": "User logged out", "session": "Session ended"}), 200

if __name__ == "__main__":
    app.run(debug=True)
