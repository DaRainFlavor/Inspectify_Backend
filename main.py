import os
from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),  # Railway provides this as an environment variable
    'user': os.getenv('DB_USER'),  # Railway provides this as an environment variable
    'password': os.getenv('DB_PASSWORD'),  # Railway provides this as an environment variable
    'database': os.getenv('DB_NAME'),  # Railway provides this as an environment variable
    'port': os.getenv('DB_PORT', 3306)  # Default MySQL port is 3306
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def hello():
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