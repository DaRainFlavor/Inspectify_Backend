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

@app.route('/')
def hello():
    # Check for API key in the request headers
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch all rows from the Users table
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()

        # Close the connection
        cursor.close()
        connection.close()

        # Return the data as JSON
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))