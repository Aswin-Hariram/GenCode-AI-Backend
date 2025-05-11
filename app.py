from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from topic_manager import get_random_topic
from question_generator import generate_dsa_question
from codeCompiler import compile_code
from submitCode import submit_code
import os
import logging
from logging.handlers import RotatingFileHandler
import traceback
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File handler for logging
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'), 
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console handler for logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Create Flask app
app = Flask(__name__)

# Configure app based on environment
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')

if ENVIRONMENT == 'production':
    # Production settings
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
        CORS_ORIGINS=os.getenv('CORS_ORIGINS', '').split(','),
    )
    # Apply ProxyFix for proper handling of reverse proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    logging.info("Running in PRODUCTION mode")
else:
    # Development settings
    app.config.update(
        CORS_ORIGINS=['http://localhost:3000'],
    )
    logging.info("Running in DEVELOPMENT mode")

# Configure CORS
CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}}, supports_credentials=True)

# Constants
TOPICS_FILE = os.getenv('TOPICS_FILE', 'dsa_topics.txt')

def read_topics():
    """Read all topics from the topics file."""
    try:
        if not os.path.exists(TOPICS_FILE):
            logging.warning(f"Topics file not found: {TOPICS_FILE}")
            return []
        
        with open(TOPICS_FILE, 'r') as file:
            topics = file.readlines()
        
        # Clean up topics (remove whitespace and empty lines)
        return [topic.strip() for topic in topics if topic.strip()]
    except Exception as e:
        logging.error(f"Error reading topics file: {str(e)}")
        return []

def write_topics(topics):
    """Write topics to the topics file."""
    try:
        with open(TOPICS_FILE, 'w') as file:
            for topic in topics:
                file.write(f"{topic}\n")
        logging.info(f"Successfully wrote {len(topics)} topics to {TOPICS_FILE}")
        return True
    except Exception as e:
        logging.error(f"Error writing topics to file: {str(e)}")
        return False



@app.route('/submit', methods=['POST'])
def submit():
    """Handle code submission and evaluation."""
    if not request.is_json:
        logging.warning("Invalid request format: not JSON")
        return jsonify({
            'result': 'Failure',
            'message': 'Invalid request format. JSON required.'
        }), 400
        
    # Retrieve code from the request body
    try:
        actualSolution = request.json.get('actualSolution')
        description = request.json.get('description')
        typedSolution = request.json.get('typedSolution')
        typedLanguage = request.json.get('language')
        
        # Validate required fields
        if not all([description, typedSolution, typedLanguage]):
            logging.warning("Missing required fields in submission")
            return jsonify({
                'result': 'Failure',
                'message': 'Missing required fields in submission.'
            }), 400

        # Pass the code to submit_code function
        logging.info(f"Processing code submission in {typedLanguage}")
        result = submit_code(typedSolution, description, typedSolution, typedLanguage)

        # Check the result and respond accordingly
        return jsonify(result)

    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"Error in code submission: {str(e)}\n{error_details}")
        return jsonify({
            'result': 'Failure',
            'message': f'Error while processing submission: {str(e)}'
        }), 500


@app.route('/compiler', methods=['POST'])
def compile():
    """Compile and run code."""
    if not request.is_json:
        logging.warning("Invalid request format: not JSON")
        return jsonify({
            'result': 'Failure',
            'message': 'Invalid request format. JSON required.'
        }), 400
        
    try:
        # Retrieve code from the request body
        lang = request.json.get('lang')
        code = request.json.get('code')
        
        # Validate required fields
        if not lang or not code:
            logging.warning("Missing required fields for compilation")
            return jsonify({
                'result': 'Failure',
                'message': 'Both language and code are required.'
            }), 400

        # Pass the code to compile_code function
        logging.info(f"Compiling code in {lang}")
        result = compile_code(code, lang)

        # Check the result and respond accordingly
        return jsonify(result)

    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"Error during compilation: {str(e)}\n{error_details}")
        return jsonify({
            'result': 'Failure',
            'message': f'Error while compiling: {str(e)}'
        }), 500

@app.route('/get_dsa_question', methods=['GET'])
def get_dsa_question():
    """Generate a random DSA question based on a topic."""
    try:
        topic = get_random_topic(TOPICS_FILE)
        if not topic:
            logging.warning("No topics found or error retrieving topic")
            return jsonify({
                'error': 'No topics available. Please add topics first.'
            }), 404
            
        logging.info(f"Generating DSA question for topic: {topic}")
        result = generate_dsa_question(topic)
        return jsonify(result)
    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"Error generating DSA question: {str(e)}\n{error_details}")
        return jsonify({
            'error': f'Failed to generate question: {str(e)}'
        }), 500

@app.route('/manage_topics')
def manage_topics():
    """Display the topics management page."""
    try:
        topics = read_topics()
        logging.info(f"Displaying manage_topics page with {len(topics)} topics")
        return render_template('manage_topics.html', topics=topics)
    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"Error displaying manage_topics page: {str(e)}\n{error_details}")
        return render_template('error.html', error=str(e)), 500

@app.route('/add_topic', methods=['POST'])
def add_topic():
    """Add a new topic to the topics file."""
    try:
        new_topic = request.form.get('new_topic', '').strip()
        
        if not new_topic:
            logging.warning("Attempted to add empty topic")
            return render_template('manage_topics.html', 
                                topics=read_topics(), 
                                message="Topic cannot be empty", 
                                success=False)
        
        topics = read_topics()
        
        # Check if topic already exists
        if new_topic in topics:
            logging.info(f"Topic '{new_topic}' already exists")
            return render_template('manage_topics.html', 
                                topics=topics, 
                                message=f"Topic '{new_topic}' already exists", 
                                success=False)
        
        # Add the new topic
        topics.append(new_topic)
        if write_topics(topics):
            logging.info(f"Topic '{new_topic}' added successfully")
            return render_template('manage_topics.html', 
                                topics=topics, 
                                message=f"Topic '{new_topic}' added successfully", 
                                success=True)
        else:
            logging.error(f"Failed to write topics after adding '{new_topic}'")
            return render_template('manage_topics.html', 
                                topics=read_topics(), 
                                message=f"Failed to add topic due to a system error", 
                                success=False)
    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"Error adding topic: {str(e)}\n{error_details}")
        return render_template('manage_topics.html', 
                            topics=read_topics(), 
                            message=f"Error adding topic: {str(e)}", 
                            success=False)

@app.route('/remove_topic', methods=['POST'])
def remove_topic():
    """Remove a topic from the topics file."""
    try:
        topic_to_remove = request.form.get('topic', '').strip()
        
        if not topic_to_remove:
            logging.warning("Attempted to remove topic without specifying which one")
            return render_template('manage_topics.html', 
                                topics=read_topics(), 
                                message="No topic specified for removal", 
                                success=False)
        
        topics = read_topics()
        
        # Check if topic exists
        if topic_to_remove not in topics:
            logging.info(f"Topic '{topic_to_remove}' not found for removal")
            return render_template('manage_topics.html', 
                                topics=topics, 
                                message=f"Topic '{topic_to_remove}' not found", 
                                success=False)
        
        # Remove the topic
        topics.remove(topic_to_remove)
        if write_topics(topics):
            logging.info(f"Topic '{topic_to_remove}' removed successfully")
            return render_template('manage_topics.html', 
                                topics=topics, 
                                message=f"Topic '{topic_to_remove}' removed successfully", 
                                success=True)
        else:
            logging.error(f"Failed to write topics after removing '{topic_to_remove}'")
            return render_template('manage_topics.html', 
                                topics=read_topics(), 
                                message=f"Failed to remove topic due to a system error", 
                                success=False)
    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"Error removing topic: {str(e)}\n{error_details}")
        return render_template('manage_topics.html', 
                            topics=read_topics(), 
                            message=f"Error removing topic: {str(e)}", 
                            success=False)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    logging.warning(f"404 error: {request.path}")
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    logging.error(f"500 error: {str(e)}")
    return render_template('error.html', error="Internal server error"), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))  # Default to 8000 for local dev
    app.run(host="0.0.0.0", port=port)
