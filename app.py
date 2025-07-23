from flask import Flask, render_template, request, jsonify, session
from chatbot import answer_query
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-key')

@app.route('/')
def index():
    # Reset history on each page load/refresh
    session['history'] = ["CONVERSATION HISTORY:"]
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or initialize history from session
        if 'history' not in session:
            session['history'] = ["CONVERSATION HISTORY:"]
        
        history = session['history']
        
        # Get response from chatbot
        bot_response = answer_query(user_message, history)
        
        # Update history in session
        history.append(f'user: {user_message}\nbot: {bot_response}')
        session['history'] = history
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
