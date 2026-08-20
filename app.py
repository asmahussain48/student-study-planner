from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import init_db, add_user, get_user, add_task, get_user_tasks, update_task, delete_task, get_task_by_id
from auth import hash_password, verify_password, is_logged_in
from ai import get_study_plan, get_mock_study_plan, test_api_key
from report import generate_pdf_report
from functools import wraps
import os
from dotenv import load_dotenv

# Load environment variables from a local .env file (if present)
# Install with: pip install python-dotenv
load_dotenv()

from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize database
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in(session):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============= AUTH ROUTES =============

@app.route('/')
def index():
    if is_logged_in(session):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password:
            return render_template('register.html', error='All fields are required')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if get_user(email):
            return render_template('register.html', error='Email already registered')
        
        hashed_pwd = hash_password(password)
        add_user(name, email, hashed_pwd)
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = get_user(email)
        
        if user and verify_password(password, user[3]):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ============= DASHBOARD & TASKS =============

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    tasks = get_user_tasks(user_id)
    
    total = len(tasks)
    completed = len([t for t in tasks if t[5] == 'completed'])
    pending = total - completed
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    stats = {
        'total': total,
        'completed': completed,
        'pending': pending,
        'completion_rate': round(completion_rate, 1)
    }
    
    return render_template('dashboard.html', tasks=tasks, stats=stats)

@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = session['user_id']
    tasks = get_user_tasks(user_id)
    
    tasks_list = []
    for task in tasks:
        tasks_list.append({
            'id': task[0],
            'user_id': task[1],
            'title': task[2],
            'description': task[3],
            'deadline': task[4],
            'status': task[5]
        })
    
    return jsonify(tasks_list)

@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    user_id = session['user_id']
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description', '')
    deadline = data.get('deadline')
    
    if not title or not deadline:
        return jsonify({'error': 'Title and deadline are required'}), 400
    
    add_task(user_id, title, description, deadline, 'pending')
    
    return jsonify({'message': 'Task created successfully'}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task_route(task_id):
    user_id = session['user_id']
    data = request.get_json()
    
    task = get_task_by_id(task_id, user_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    status = data.get('status', task[5])
    update_task(task_id, status)
    
    return jsonify({'message': 'Task updated'}), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task_route(task_id):
    user_id = session['user_id']
    
    task = get_task_by_id(task_id, user_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    delete_task(task_id)
    
    return jsonify({'message': 'Task deleted'}), 200

# ============= AI ASSISTANT =============

@app.route('/assistant')
@login_required
def assistant():
    return render_template('assistant.html')

@app.route('/api/ai/study-plan', methods=['POST'])
@login_required
def ai_study_plan():
    user_id = session['user_id']
    data = request.get_json()
    
    prompt = data.get('prompt')
    tasks = get_user_tasks(user_id)
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Get AI response
    response = get_study_plan(prompt, tasks)

    # If the AI layer returned an error-like string (our ai.py prefixes with ⚠️),
    # return the error and a suggestion (mock) but do NOT silently replace the response.
    if isinstance(response, str) and response.startswith('⚠️'):
        # Log the error server-side for debugging
        app.logger.error('AI backend error: %s', response)
        suggestion = get_mock_study_plan(prompt, tasks)
        return jsonify({'error': response, 'suggestion': suggestion}), 200

    # Successful model output
    return jsonify({'response': response}), 200

# ============= PDF REPORT =============

@app.route('/report')
@login_required
def report():
    user_id = session['user_id']
    user_name = session['user_name']
    tasks = get_user_tasks(user_id)
    
    # Generate PDF
    pdf_path = generate_pdf_report(user_name, tasks)
    
    # Return download
    return redirect(url_for('static', filename=f'../reports/{os.path.basename(pdf_path)}'))

@app.route('/api/report/generate', methods=['GET'])
@login_required
def generate_report():
    user_id = session['user_id']
    user_name = session['user_name']
    tasks = get_user_tasks(user_id)
    
    pdf_path = generate_pdf_report(user_name, tasks)
    
    return jsonify({
        'message': 'Report generated',
        'file': os.path.basename(pdf_path)
    }), 200

@app.route('/reports/<filename>')
@login_required
def download_report(filename):
    from flask import send_file
    file_path = os.path.join('reports', filename)
    return send_file(file_path, as_attachment=True)


# ============= DEBUG / DIAGNOSTICS =============
@app.route('/debug/test-api')
@login_required
def debug_test_api():
    """Test the Google Generative AI API key and return a JSON result from test_api_key().
    Protected by login_required so only authenticated users can call it.
    """
    result = test_api_key()
    status_code = 200 if result.get('ok') else 400
    return jsonify(result), status_code


@app.route('/debug/list-models')
@login_required
def debug_list_models():
    """List the Generative Language models accessible to the configured API key."""
    key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not key:
        return jsonify({'ok': False, 'error': 'GEMINI_API_KEY (or GOOGLE_API_KEY) not set in environment'}), 400
    ok, data = list_models(key)
    if ok:
        return jsonify({'ok': True, 'models': data}), 200
    return jsonify({'ok': False, 'error': data}), 400

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Startup check: warn if GOOGLE_API_KEY not set (do not print the key itself)
    if not (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')):
        app.logger.warning('GEMINI_API_KEY (or GOOGLE_API_KEY) is not set. AI calls will fail until you set it in your environment or .env file.')
    else:
        app.logger.info('GEMINI_API_KEY is set (hidden). AI features will attempt to use it.')
    app.run(debug=True, port=5000)
