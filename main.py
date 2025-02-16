import os
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO
from chat import ChatHandler
from scraper import get_website_content

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
socketio = SocketIO(app)

# Initialize chat handler
chat_handler = ChatHandler()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(message):
    try:
        response = chat_handler.get_response(message)
        socketio.emit('response', {'message': response})
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        socketio.emit('error', {'message': 'An error occurred processing your request'})

if __name__ == '__main__':
    # Load website content on startup
    website_content = get_website_content("https://www.thevermafamily.org")
    chat_handler.initialize_context(website_content)
    
    # Start server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
