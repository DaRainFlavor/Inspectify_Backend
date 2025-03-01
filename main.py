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
    """Create a sample table if it does not exist."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SampleTable (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized: SampleTable created (if not exists)")
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

if __name__ == '__main__':
    initialize_database()  # Ensure the table exists before running the app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
