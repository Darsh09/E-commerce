from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


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

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/register", methods = ['POST'])
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
        return jsonify({'message': 'User Already Eists'}), 409
    else:
        cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s);', (email, password))
        conn.commit()
        return jsonify({'message': 'User created'}), 200
    
@app.route("/login", methods = ['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    email = data.get("email")
    password = data.get("password")

    cursor.execute("SELECT 1 FROM users WHERE email = %s AND password=%s;", (email, password))

    user = cursor.fetchone()

    if user:
        return jsonify({"message": "User logged in"}), 200
    else:
        return jsonify({"message": "User not found"}), 404
    


