import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
from models import db, ChatMessage, User
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

def get_client_ip():
    """Get client IP address from request"""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('register'))
    return render_template('chat.html')

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    try:
        # Get user data from form
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        ip_address = get_client_ip()

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            session['user_id'] = existing_user.id
            return redirect(url_for('index'))

        # Create new user
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            ip_address=ip_address
        )
        db.session.add(user)
        db.session.commit()

        # Store user ID in session
        session['user_id'] = user.id
        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return "Registration failed. Please try again.", 400

@socketio.on('message')
def handle_message(data):
    try:
        if 'user_id' not in session:
            socketio.emit('error', {'message': 'Please register or login first'})
            return

        if isinstance(data, dict):
            message = data.get('text', '')
            language = data.get('language', 'en')
        else:
            message = str(data)
            language = 'en'

        response = chat_handler.get_response(message, target_lang=language)

        # Store the message in database
        chat_message = ChatMessage(
            user_id=session['user_id'],
            message=message,
            response=response,
            language=language
        )
        db.session.add(chat_message)
        db.session.commit()

        socketio.emit('response', {'message': response})
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        socketio.emit('error', {'message': 'An error occurred processing your request'})

@socketio.on('set_language')
def handle_language_change(language):
    logger.info(f"Language changed to: {language}")

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()

        # Define multiple starting URLs for the website
        start_urls = [
            "https://www.thevermafamily.org",
            "https://thevermafamily.org/about-us",
            "https://thevermafamily.org/late-shrikant-verma",
            "https://thevermafamily.org/late-veena-verma",
            "https://thevermafamily.org/abhishek-verma",
            "https://thevermafamily.org/anca-verma",
            "https://thevermafamily.org/nicolle-verma",
            "https://thevermafamily.org/aditeshwar-verma",
            "https://thevermafamily.org/blogs/",
            "https://thevermafamily.org/contact-us",
        ]

        # Load website content on startup with increased page limit
        logger.info("Starting website content extraction...")
        website_content = ""
        for url in start_urls:
            logger.info(f"Processing starting URL: {url}")
            content = get_website_content(url, max_pages=100)
            if content:
                website_content += f"\n\n{content}"
        logger.info("Website content extraction completed")

        if website_content:
            chat_handler.initialize_context(website_content)
            logger.info("Chat handler initialized with website content")
        else:
            logger.error("Failed to extract website content")

    # Start server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)