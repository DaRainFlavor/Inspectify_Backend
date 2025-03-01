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

@app.route('/init_db')
def init_db():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    initialize_database()
    return jsonify({"message": "Database initialized."})

@app.route('/homeowners', methods=['GET'])
def get_homeowners():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Homeowner")
    all_homeowners = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(all_homeowners)

@app.route('/homeowners/<homeowner_id>', methods=['GET'])
def get_homeowner(homeowner_id):
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Homeowner WHERE homeowner_id = %s", (homeowner_id,))
    homeowner = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify(homeowner)

@app.route('/homeowners', methods=['POST'])
def add_homeowner():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    homeowner_id = request.json['homeowner_id']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Homeowner (homeowner_id) VALUES (%s)", (homeowner_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"homeowner_id": homeowner_id})

@app.route('/homes', methods=['GET'])
def get_homes():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Home")
    all_homes = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(all_homes)

@app.route('/homes/<homeowner_id>', methods=['GET'])
def get_homes_by_homeowner(homeowner_id):
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Home WHERE homeowner_id = %s", (homeowner_id,))
    homes = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(homes)

@app.route('/homes', methods=['POST'])
def add_home():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.json
        homeowner_id = data['homeowner_id']
        home_name = data['homeName']
        house_age = int(data['houseAge']) if data['houseAge'] is not None else None
        house_use = data['houseUse']
        renovations = data.get('renovations', None)
        type_of_house = data['typeOfHouse']
        num_floor = int(data['numFloor']) if data['numFloor'] is not None else None
        lot_area = float(data['lotArea']) if data['lotArea'] is not None else None
        floor_area = float(data['floorArea']) if data['floorArea'] is not None else None
        selected_house_type = data['selectedHouseType']
        selected_material = data['selectedMaterial']
        selected_flooring = data['selectedFlooring']
        selected_wall = data['selectedWall']
        selected_ceiling = data['selectedCeiling']
        latitude = float(data.get('latitude', 0)) if data.get('latitude') is not None else None
        longitude = float(data.get('longitude', 0)) if data.get('longitude') is not None else None
        is_default = data.get('is_default', False)

        connection = get_db_connection()
        cursor = connection.cursor()

        # Set all existing homes of the homeowner to non-default if the new home is default
        if is_default:
            cursor.execute("UPDATE Home SET is_default = FALSE WHERE homeowner_id = %s", (homeowner_id,))

        cursor.execute("""
            INSERT INTO Home (
                homeowner_id, home_name, house_age, house_use, renovations, type_of_house, num_floor, lot_area, floor_area,
                selected_house_type, selected_material, selected_flooring, selected_wall, selected_ceiling, latitude, longitude, is_default
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            homeowner_id, home_name, house_age, house_use, renovations, type_of_house, num_floor, lot_area, floor_area,
            selected_house_type, selected_material, selected_flooring, selected_wall, selected_ceiling, latitude, longitude, is_default
        ))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "Home added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/homeowners/<homeowner_id>/default_home', methods=['GET'])
def get_default_home(homeowner_id):
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT home_name, latitude, longitude FROM Home WHERE homeowner_id = %s AND is_default = TRUE", (homeowner_id,))
    default_home = cursor.fetchone()
    cursor.close()
    connection.close()
    if default_home:
        return jsonify(default_home)
    else:
        return jsonify({'message': 'No default home found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))