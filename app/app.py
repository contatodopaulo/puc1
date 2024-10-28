from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow requests from your domain
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://puc1.paulogontijo.com"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://puc1.paulogontijo.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'signup_db')
}

# Create database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Create the users table if it doesn't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            remember_me BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Initialize the database when the app starts
init_db()

@app.route('/api/signup', methods=['POST', 'OPTIONS'])
def signup():
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        return '', 200
        
    # Your existing signup code for POST requests
    try:
        data = request.get_json()
        
        # Extract data from request
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember', False)
        
        # Validate required fields
        if not all([name, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert user into database
        try:
            cursor.execute('''
                INSERT INTO users (name, email, password, remember_me)
                VALUES (%s, %s, %s, %s)
            ''', (name, email, hashed_password, remember))
            
            conn.commit()
            
            return jsonify({
                'message': 'User registered successfully',
                'user': {
                    'name': name,
                    'email': email,
                    'remember': remember
                }
            }), 201
            
        except mysql.connector.IntegrityError as e:
            return jsonify({'error': 'Email already exists'}), 409
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2053, debug=True)
