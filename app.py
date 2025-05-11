from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from topic_manager import get_random_topic
from question_generator import generate_dsa_question
from codeCompiler import compile_code
from submitCode import submit_code
import os
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app, resources={r"/*": {"origins": "*"}})


# Constants
TOPICS_FILE = os.getenv('TOPICS_FILE', 'dsa_topics.txt')

def read_topics():
    """Read all topics from the topics file."""
    try:
        if not os.path.exists(TOPICS_FILE):
           
            return []
        
        with open(TOPICS_FILE, 'r') as file:
            topics = file.readlines()
        
        # Clean up topics (remove whitespace and empty lines)
        return [topic.strip() for topic in topics if topic.strip()]
    except Exception as e:
        # Error reading topics file
        return []

def write_topics(topics):
    """Write topics to the topics file."""
    try:
        with open(TOPICS_FILE, 'w') as file:
            for topic in topics:
                file.write(f"{topic}\n")
        # Successfully wrote topics
        return True
    except Exception as e:
        # Error writing topics to file
        return False



@app.route('/submit', methods=['POST'])
def submit():
    """Handle code submission and evaluation."""
    if not request.is_json:
        # Invalid request format
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
            # Missing required fields
            return jsonify({
                'result': 'Failure',
                'message': 'Missing required fields in submission.'
            }), 400

        # Pass the code to submit_code function
        # Processing code submission
        result = submit_code(typedSolution, description, typedSolution, typedLanguage)

        # Check the result and respond accordingly
        return jsonify(result)

    except Exception as e:
        error_details = traceback.format_exc()
        # Error in code submission
        return jsonify({
            'result': 'Failure',
            'message': f'Error while processing submission: {str(e)}'
        }), 500


@app.route('/compiler', methods=['POST'])
def compile():
    """Compile and run code."""
    if not request.is_json:
        # Invalid request format
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
            # Missing required fields for compilation
            return jsonify({
                'result': 'Failure',
                'message': 'Both language and code are required.'
            }), 400

        # Pass the code to compile_code function
        # Compiling code
        result = compile_code(code, lang)

        # Check the result and respond accordingly
        return jsonify(result)

    except Exception as e:
        error_details = traceback.format_exc()
        # Error during compilation
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
            # No topics found
            return jsonify({
                'error': 'No topics available. Please add topics first.'
            }), 404
            
        # Generating DSA question
        result = generate_dsa_question(topic)
        return jsonify(result)
    except Exception as e:
        error_details = traceback.format_exc()
        # Error generating DSA question
        return jsonify({
            'error': f'Failed to generate question: {str(e)}'
        }), 500

@app.route('/manage_topics')
def manage_topics():
    """Display the topics management page."""
    try:
        topics = read_topics()
        # Displaying manage_topics page
        return render_template('manage_topics.html', topics=topics)
    except Exception as e:
        error_details = traceback.format_exc()
        # Error displaying manage_topics page
        return render_template('error.html', error=str(e)), 500

@app.route('/add_topic', methods=['POST'])
def add_topic():
    """Add a new topic to the topics file."""
    try:
        new_topic = request.form.get('new_topic', '').strip()
        
        if not new_topic:
            # Attempted to add empty topic
            return render_template('manage_topics.html', 
                                topics=read_topics(), 
                                message="Topic cannot be empty", 
                                success=False)
        
        topics = read_topics()
        
        # Check if topic already exists
        if new_topic in topics:
            # Topic already exists
            return render_template('manage_topics.html', 
                                topics=topics, 
                                message=f"Topic '{new_topic}' already exists", 
                                success=False)
        
        # Add the new topic
        topics.append(new_topic)
        if write_topics(topics):
            # Topic added successfully
            return render_template('manage_topics.html', 
                                topics=topics, 
                                message=f"Topic '{new_topic}' added successfully", 
                                success=True)
        else:
            # Failed to write topics
            return render_template('manage_topics.html', 
                                topics=read_topics(), 
                                message=f"Failed to add topic due to a system error", 
                                success=False)
    except Exception as e:
        error_details = traceback.format_exc()
        # Error adding topic
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
            # Attempted to remove topic without specifying which one
            return render_template('manage_topics.html', 
                                topics=read_topics(), 
                                message="No topic specified for removal", 
                                success=False)
        
        topics = read_topics()
        
        # Check if topic exists
        if topic_to_remove not in topics:
            # Topic not found for removal
            return render_template('manage_topics.html', 
                                topics=topics, 
                                message=f"Topic '{topic_to_remove}' not found", 
                                success=False)
        
        # Remove the topic
        topics.remove(topic_to_remove)
        if write_topics(topics):
            # Topic removed successfully
            return render_template('manage_topics.html', 
                                topics=topics, 
                                message=f"Topic '{topic_to_remove}' removed successfully", 
                                success=True)
        else:
            # Failed to write topics after removing
            return render_template('manage_topics.html', 
                                topics=read_topics(), 
                                message=f"Failed to remove topic due to a system error", 
                                success=False)
    except Exception as e:
        error_details = traceback.format_exc()
        # Error removing topic
        return render_template('manage_topics.html', 
                            topics=read_topics(), 
                            message=f"Error removing topic: {str(e)}", 
                            success=False)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    # 404 error
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    # 500 error
    return render_template('error.html', error="Internal server error"), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Root path handler
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))  # Default to 8001 for local dev
    app.run(host="0.0.0.0", port=port)
