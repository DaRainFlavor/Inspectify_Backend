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
    """Drop existing tables and recreate Homeowner and Home tables"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Drop tables if they exist
        cursor.execute("DROP TABLE IF EXISTS Home;")
        cursor.execute("DROP TABLE IF EXISTS Homeowner;")

        # Recreate Homeowner table
        cursor.execute("""
            CREATE TABLE Homeowner (
                homeowner_id VARCHAR(50) PRIMARY KEY
            );
        """)

        # Recreate Home table
        cursor.execute("""
            CREATE TABLE Home (
                home_id INT PRIMARY KEY AUTO_INCREMENT,
                homeowner_id VARCHAR(50) NOT NULL,
                home_name VARCHAR(100) NOT NULL,
                house_age INT NULL,
                house_use VARCHAR(100) NULL,
                renovations TEXT NULL,
                type_of_house VARCHAR(100) NULL,
                num_floor INT NULL,
                lot_area FLOAT NULL,
                floor_area FLOAT NULL,
                selected_house_type VARCHAR(100) NULL,
                selected_material VARCHAR(100) NULL,
                selected_flooring VARCHAR(100) NULL,
                selected_wall VARCHAR(100) NULL,
                selected_ceiling VARCHAR(100) NULL,
                latitude FLOAT NULL,
                longitude FLOAT NULL,
                is_default BOOLEAN NOT NULL DEFAULT FALSE,
                date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (homeowner_id) REFERENCES Homeowner(homeowner_id) ON DELETE CASCADE
            );
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized: Homeowner and Home tables recreated successfully.")
    
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

@app.route('/init_db')
def init_db():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    initialize_database()
    return jsonify({"message": "Database initialized."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
