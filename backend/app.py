from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from database import (
    init_db, add_booth, add_voter, get_all_booths, 
    get_voters_by_booth, search_voters, update_voter, 
    get_voter_stats, clear_all_data
)
from pdf_parser import extract_voters_from_pdf

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
    template_folder=os.path.join(base_dir, 'frontend', 'templates'),
    static_folder=os.path.join(base_dir, 'frontend', 'static'))
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"]
    }
})

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database on startup
init_db()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/booths', methods=['GET'])
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
def update_voter_info(voter_id):
    """Update voter information"""
    try:
        data = request.get_json()
        status = data.get('status')
        custom_notes = data.get('custom_notes')
        
        if not status and not custom_notes:
            return jsonify({
                'status': 'error',
                'message': 'At least one field must be provided'
            }), 400
        
        update_voter(voter_id, status, custom_notes)
        
        return jsonify({
            'status': 'success',
            'message': 'Voter updated successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload and parse voter list PDF"""
    try:
        # Check if file is present
        if 'pdf_file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': 'Only PDF files are allowed'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse PDF
        voters, booths = extract_voters_from_pdf(filepath)
        
        if not voters:
            os.remove(filepath)
            return jsonify({
                'status': 'error',
                'message': 'Could not extract voter data from PDF. Please ensure it contains voter information with columns for Name, Voter ID (EPIC), and Booth Number.'
            }), 400
        
        # Add booths and voters to database
        booth_ids = {}
        for booth_num in booths:
            booth_id = add_booth(booth_num, f'Booth {booth_num}')
            booth_ids[booth_num] = booth_id
        
        added_voters = 0
        skipped_voters = 0
        
        for voter in voters:
            if add_voter(voter['voter_id'], voter['voter_name'], voter['booth_number']):
                added_voters += 1
            else:
                skipped_voters += 1
        
        # Clean up uploaded file after processing
        os.remove(filepath)
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully added {added_voters} voters',
            'added_voters': added_voters,
            'skipped_voters': skipped_voters,
            'total_booths': len(booths)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing PDF: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
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
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("Starting Voter Data Management System...")
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"Backend running at http://0.0.0.0:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
