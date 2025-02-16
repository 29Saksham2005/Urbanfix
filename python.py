from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import mysql.connector
import logging
from dotenv import load_dotenv

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configure upload folder (where images will be saved)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upload.log'),  # Separate log file for clarity
        logging.StreamHandler()  # Still log to console
    ]
)
logger = logging.getLogger(__name__)

# Add a test log message at startup
logger.info("Application started")
logger.info(f"Upload folder is set to: {UPLOAD_FOLDER}")
logger.info(f"Allowed extensions are: {ALLOWED_EXTENSIONS}")

# After UPLOAD_FOLDER definition
logger.info("=== Checking upload directory ===")

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER, mode=0o777)  # Full permissions for testing
        logger.info(f"Created upload directory: {UPLOAD_FOLDER}")
    except Exception as e:
        logger.error(f"Failed to create upload directory: {e}")

# Check directory permissions
try:
    test_path = os.path.abspath(UPLOAD_FOLDER)
    logger.info(f"Absolute path to upload directory: {test_path}")
    logger.info(f"Directory exists: {os.path.exists(test_path)}")
    logger.info(f"Is directory: {os.path.isdir(test_path)}")
    logger.info(f"Directory permissions: {oct(os.stat(test_path).st_mode)[-3:]}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Directory writable: {os.access(test_path, os.W_OK)}")
except Exception as e:
    logger.error(f"Error checking directory permissions: {e}")

load_dotenv()  # Load environment variables from .env file

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INT AUTO_INCREMENT PRIMARY KEY,
                image_filename VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                category VARCHAR(100) NOT NULL
            )
        ''')
        conn.commit()
    except mysql.connector.Error as e:
        print(f"An error occurred while initializing the database: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logger.info("=== Starting new file upload via standard form ===")
        try:
            logger.info(f"Form data: {request.form}")
            logger.info(f"Files: {request.files}")
            
            if 'image' not in request.files:
                logger.error("No image file in request")
                flash('No image file uploaded')
                return render_template('user.html')

            image = request.files['image']
            description = request.form.get('description', '')
            category = request.form.get('category', '')

            if image.filename == '':
                logger.error("Empty filename")
                flash('No file selected')
                return render_template('user.html')

            if not allowed_file(image.filename):
                logger.error(f"Invalid file type: {image.filename}")
                flash('Invalid file type. Please upload an image.')
                return render_template('user.html')

            # Create a safe filename
            filename = secure_filename(image.filename)
            logger.info(f"Secure filename created: {filename}")

            # Ensure upload directory exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                logger.info("Creating upload directory")
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            # Save the file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logger.info(f"Attempting to save file to: {file_path}")
            
            try:
                image.save(file_path)
                logger.info("File saved successfully")
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}")
                flash('Error saving file')
                return render_template('user.html')

            # Database operations
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO complaints (image_filename, description, category) VALUES (%s, %s, %s)',
                    (filename, description, category)
                )
                conn.commit()
                logger.info("Database entry created successfully")
                flash('Complaint submitted successfully!')
            except mysql.connector.Error as e:
                logger.error(f"Database error: {str(e)}")
                flash('Error saving to database')
                return render_template('user.html')
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

            return redirect(url_for('index'))

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            flash('An unexpected error occurred')
            return render_template('user.html')

    return render_template('user.html')

@app.route('/submit_complaint', methods=['GET', 'POST'])
def submit_complaint():
    logger.info(f"=== Received {request.method} request to /submit_complaint ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request files: {request.files}")
    logger.info(f"Request form: {request.form}")

    if request.method != 'POST':
        logger.error(f"Invalid method: {request.method}")
        return jsonify({'error': 'Method not allowed'}), 405

    try:
        if 'image' not in request.files:
            logger.error("No image in request")
            return jsonify({'error': 'No image uploaded'}), 400

        image = request.files['image']
        logger.info(f"Received file: {image.filename}")
        
        description = request.form.get('description', '')
        category = request.form.get('category', '')

        logger.info(f"Description: {description}")
        logger.info(f"Category: {category}")

        if image.filename == '':
            logger.error("Empty filename in AJAX request")
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(image.filename):
            logger.error(f"Invalid file type in AJAX request: {image.filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        filename = secure_filename(image.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Attempting to save file to: {file_path}")
        
        # Ensure directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            logger.info(f"Creating upload directory: {app.config['UPLOAD_FOLDER']}")
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Check directory permissions
        try:
            test_path = os.path.abspath(app.config['UPLOAD_FOLDER'])
            logger.info(f"Directory exists: {os.path.exists(test_path)}")
            logger.info(f"Is directory: {os.path.isdir(test_path)}")
            logger.info(f"Directory permissions: {oct(os.stat(test_path).st_mode)[-3:]}")
            logger.info(f"Directory writable: {os.access(test_path, os.W_OK)}")
        except Exception as e:
            logger.error(f"Error checking directory permissions: {e}")

        try:
            # First, ensure the file stream is at the beginning
            image.stream.seek(0)
            
            # Save with explicit file handling
            with open(file_path, 'wb') as f:
                # Copy the file in chunks to handle large files
                chunk_size = 8192  # 8KB chunks
                while True:
                    chunk = image.stream.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    f.flush()  # Ensure data is written to disk
            
            logger.info(f"File saved successfully: {file_path}")
            
            # Verify file was saved
            if os.path.exists(file_path):
                logger.info(f"File exists after save, size: {os.path.getsize(file_path)} bytes")
            else:
                logger.error("File does not exist after save attempt")
                return jsonify({'error': 'File failed to save'}), 500

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({'error': f'Error saving file: {str(e)}'}), 500

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO complaints (image_filename, description, category) VALUES (%s, %s, %s)',
                (filename, description, category)
            )
            conn.commit()
            logger.info("Database entry created successfully")
            return jsonify({'message': 'Complaint submitted successfully'}), 200
        except mysql.connector.Error as e:
            logger.error(f"Database error: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# Make sure this is at the bottom of your file
if __name__ == '__main__':
    init_db()
    app.run(debug=True)'''