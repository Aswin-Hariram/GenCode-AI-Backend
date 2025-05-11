from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

TOPICS_FILE = 'dsa_topics.txt'

def read_topics():
    """Read all topics from the topics file."""
    if not os.path.exists(TOPICS_FILE):
        return []
    
    with open(TOPICS_FILE, 'r') as file:
        topics = file.readlines()
    
    # Clean up topics (remove whitespace and empty lines)
    return [topic.strip() for topic in topics if topic.strip()]

def write_topics(topics):
    """Write topics to the topics file."""
    with open(TOPICS_FILE, 'w') as file:
        for topic in topics:
            file.write(f"{topic}\n")

@app.route('/')
def index():
    """Display the topics management page."""
    topics = read_topics()
    return render_template('manage_topics.html', topics=topics)

@app.route('/add_topic', methods=['POST'])
def add_topic():
    """Add a new topic to the topics file."""
    new_topic = request.form.get('new_topic', '').strip()
    
    if not new_topic:
        return render_template('manage_topics.html', 
                              topics=read_topics(), 
                              message="Topic cannot be empty", 
                              success=False)
    
    topics = read_topics()
    
    # Check if topic already exists
    if new_topic in topics:
        return render_template('manage_topics.html', 
                              topics=topics, 
                              message=f"Topic '{new_topic}' already exists", 
                              success=False)
    
    # Add the new topic
    topics.append(new_topic)
    write_topics(topics)
    
    return render_template('manage_topics.html', 
                          topics=topics, 
                          message=f"Topic '{new_topic}' added successfully", 
                          success=True)

@app.route('/remove_topic', methods=['POST'])
def remove_topic():
    """Remove a topic from the topics file."""
    topic_to_remove = request.form.get('topic', '').strip()
    
    if not topic_to_remove:
        return render_template('manage_topics.html', 
                              topics=read_topics(), 
                              message="No topic specified for removal", 
                              success=False)
    
    topics = read_topics()
    
    # Check if topic exists
    if topic_to_remove not in topics:
        return render_template('manage_topics.html', 
                              topics=topics, 
                              message=f"Topic '{topic_to_remove}' not found", 
                              success=False)
    
    # Remove the topic
    topics.remove(topic_to_remove)
    write_topics(topics)
    
    return render_template('manage_topics.html', 
                          topics=topics, 
                          message=f"Topic '{topic_to_remove}' removed successfully", 
                          success=True)

if __name__ == '__main__':
    app.run(debug=True)
