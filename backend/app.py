from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
import os
import tempfile
import traceback
import uuid
import pandas as pd
import re
import click
from io import BytesIO
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from functools import wraps
from database import (
    init_db, add_booth, get_all_booths, 
    get_voters_by_booth, search_voters, update_voter, 
    get_voter_stats, clear_all_data, add_user, get_user_by_username,
    upsert_voters
)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
    template_folder=os.path.join(base_dir, 'frontend', 'templates'),
    static_folder=os.path.join(base_dir, 'frontend', 'static'))
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"]
    }
})

app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-for-flask-sessions')

# Configuration
DEFAULT_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), 'voter-management-uploads')
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', DEFAULT_UPLOAD_DIR)
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database on startup
init_db()

# ==================== AUTHENTICATION ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = get_user_by_username(username)

        if user is None or not check_password_hash(user['password'], password):
            error = 'Incorrect username or password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error=error)
    
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.cli.command('create-user')
@click.argument('username')
@click.argument('password')
def create_user_command(username, password):
    """Creates a new user for login."""
    add_user(username, password)
    print(f'User {username} created successfully.')

# ==================== PAGE ROUTES ====================

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/upload-file', methods=['POST'])
@login_required
def upload_file():
    """Upload and parse voter list from Excel or CSV"""
    filepath = None
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': 'Only .xlsx and .csv files are allowed'
            }), 400
        
        original_name = secure_filename(file.filename)
        filename = f"{uuid.uuid4().hex}_{original_name}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Use pandas to read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Normalize column names (lowercase, replace space with underscore)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Define expected columns and their mapping
        column_map = {
            'epic_number': 'voter_id',
            'name': 'voter_name',
            'house_number': 'house_number'
        }
        
        # Check for required columns
        required_cols = ['epic_number', 'name']
        if not all(col in df.columns for col in required_cols):
             return jsonify({'status': 'error', 'message': 'Missing required columns in file: EPIC Number, Name'}), 400

        df.rename(columns=column_map, inplace=True)

        # Extract booth number from filename (e.g., booth-123.xlsx)
        match = re.search(r'(\d+)', original_name)
        if match:
            booth_number = match.group(1)
            df['booth_number'] = booth_number
        else:
            return jsonify({'status': 'error', 'message': "Could not determine Booth Number. Please name your file like 'booth-123.xlsx' or 'part-42.csv'."}), 400

        # Ensure voter_id is a string
        df['voter_id'] = df['voter_id'].astype(str)

        voters_data = df.to_dict('records')
        
        added, updated = upsert_voters(voters_data)
        
        # Clean up uploaded file after processing
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully processed file. Added: {added}, Updated: {updated}',
            'added_voters': added,
            'updated_voters': updated
        })
    
    except Exception as e:
        print("Error processing file upload:")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Error processing file: {str(e)}'
        }), 500
    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

# ==================== API ROUTES ====================

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get overall statistics"""
    try:
        booths = get_all_booths()
        stats = get_voter_stats()
        
        return jsonify({
            'status': 'success',
            'total_voters': stats['total'],
            'visited_voters': stats['visited'] or 0,
            'total_booths': len(booths)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/clear-data', methods=['POST'])
@login_required
def clear_data():
    """Clear all data from database (for testing/reset)"""
    try:
        clear_all_data()
        return jsonify({
            'status': 'success',
            'message': 'All data cleared successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/booths', methods=['GET'])
@login_required
def get_booths():
    """Get all booths"""
    try:
        booths = get_all_booths()
        return jsonify({
            'status': 'success',
            'booths': booths,
            'total_booths': len(booths)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/booth/<int:booth_id>/voters', methods=['GET'])
@login_required
def get_booth_voters(booth_id):
    """Get voters for a specific booth"""
    try:
        voters = get_voters_by_booth(booth_id)
        stats = get_voter_stats(booth_id)
        
        return jsonify({
            'status': 'success',
            'voters': voters,
            'booth_stats': stats
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/search', methods=['GET'])
@login_required
def search():
    """Search voters by name or ID"""
    try:
        search_term = request.args.get('q', '').strip()
        booth_id = request.args.get('booth_id')
        
        if not search_term or len(search_term) < 2:
            return jsonify({
                'status': 'error', 
                'message': 'Search term must be at least 2 characters'
            }), 400
        
        booth_id = int(booth_id) if booth_id else None
        voters = search_voters(search_term, booth_id)
        
        return jsonify({
            'status': 'success',
            'voters': voters,
            'count': len(voters)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/voter/<int:voter_id>', methods=['PUT'])
@login_required
def update_voter_info(voter_id):
    """Update voter information"""
    try:
        data = request.get_json()
        status = data.get('status')
        phone_number = data.get('phone_number')
        custom_notes = data.get('custom_notes')
        house_number = data.get('house_number')
        
        if not any([status, phone_number, custom_notes, house_number]):
            return jsonify({
                'status': 'error',
                'message': 'At least one field must be provided'
            }), 400
        
        update_voter(voter_id, status, phone_number, custom_notes, house_number)
        
        return jsonify({
            'status': 'success',
            'message': 'Voter updated successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/export', methods=['GET'])
@login_required
def export_voters():
    """Export voters to CSV or Excel"""
    try:
        export_type = request.args.get('type', 'csv').lower()
        
        from database import get_db
        conn = get_db() 
        query = "SELECT voter_name, voter_id, house_number, booth_number, phone_number, status, custom_notes FROM voters ORDER BY booth_number, voter_name"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return jsonify({'status': 'error', 'message': 'No voters found to export'}), 404
        
        output = BytesIO()
        if export_type == 'csv':
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name='voters_export.csv')
        else: # excel
            df.to_excel(output, index=False, sheet_name='Voters')
            output.seek(0)
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='voters_export.xlsx')
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'status': 'error',
        'message': 'File too large. Maximum file size is 50MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    print("An internal server error occurred:")
    print(traceback.format_exc())
    return jsonify({
        'status': 'error',
        'message': f'Internal server error: {str(error)}'
    }), 500

if __name__ == '__main__':
    print("Starting Voter Data Management System...")
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"Backend running at http://127.0.0.1:{port}")
    print(f"Temporary upload folder: {app.config['UPLOAD_FOLDER']}")
    app.run(debug=debug, host='127.0.0.1', port=port)
