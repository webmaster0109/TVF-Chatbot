import os
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO
from models import db, ChatMessage #Import from models
from chat import ChatHandler
from scraper import get_website_content

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Initialize Socket.IO
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

        # Store the message in database
        chat_message = ChatMessage(
            message=message,
            response=response
        )
        db.session.add(chat_message)
        db.session.commit()

        socketio.emit('response', {'message': response})
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        socketio.emit('error', {'message': 'An error occurred processing your request'})

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()

        # Load website content on startup
        website_content = get_website_content("https://www.thevermafamily.org")
        chat_handler.initialize_context(website_content)

    # Start server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)