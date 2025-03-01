import os
from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv('MYSQLHOST'),  # Matches Railway variable name
    'user': os.getenv('MYSQLUSER'),
    'password': os.getenv('MYSQLPASSWORD'),
    'database': os.getenv('MYSQLDATABASE'),
    'port': int(os.getenv('MYSQLPORT', 3306))  # Convert port to integer
}

# API Key (store this in your environment variables)
API_KEY = os.getenv('API_KEY')

def get_db_connection():
    return mysql.connector.connect(**db_config)

def initialize_database():
    """Create the Users table if it does not exist."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users2 (
                id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized: Users table created (if not exists)")
    except Exception as e:
        print("Error initializing database:", e)

@app.route('/')
def hello():
    # Check for API key in the request headers
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user_id = data.get('id')
    name = data.get('name')

    if not user_id or not name:
        return jsonify({"error": "Missing id or name"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("INSERT INTO Users (id, name) VALUES (%s, %s)", (user_id, name))
        connection.commit()
        
        cursor.close()
        connection.close()
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    initialize_database()  # Ensure the Users table exists before running the app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
