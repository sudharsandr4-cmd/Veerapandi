from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import traceback
import uuid
import pandas as pd
from io import BytesIO
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
DEFAULT_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), 'voter-management-uploads')
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', DEFAULT_UPLOAD_DIR)
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
def export_voters():
    """Export voters to CSV or Excel"""
    try:
        export_type = request.args.get('type', 'csv').lower()
        filter_status = request.args.get('filter', 'all').lower()
        
        if export_type not in ['csv', 'excel']:
            return jsonify({'status': 'error', 'message': 'Type must be csv or excel'}), 400
        
        # Get all voters
        # Use the existing get_db from database.py
        from database import get_db
        conn = get_db() 
        cursor = conn.cursor()
        
        if filter_status == 'visited':
            status_condition = "WHERE status = 'visited'"
        elif filter_status == 'remaining':
            status_condition = "WHERE status != 'visited' OR status IS NULL"
        else:
            status_condition = ""
        
        cursor.execute(f'''
            SELECT voter_name, voter_id, house_number, booth_number, phone_number, status, custom_notes 
            FROM voters {status_condition}
            ORDER BY booth_number, voter_name
        ''')
        voters = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not voters:
            return jsonify({'status': 'error', 'message': 'No voters found'}), 404
        
        df = pd.DataFrame(voters)
        
        if export_type == 'csv':
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(output, mimetype='text/csv', as_attachment=True, 
                           download_name=f'voters_{filter_status}.csv')
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Voters')
            output.seek(0)
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                           as_attachment=True, download_name=f'voters_{filter_status}.xlsx')
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload and parse voter list PDF"""
    filepath = None
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
        
        # Get custom filename if provided
        custom_filename = request.form.get('custom_filename', '').strip()
        if custom_filename:
            _, ext = os.path.splitext(file.filename)
            if not ext:
                ext = '.pdf'
            filename = secure_filename(custom_filename + ext)
        else:
            original_name = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{original_name}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Receiving upload: {file.filename} -> {filepath}")
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        print(f"Saved upload ({file_size} bytes). Starting parse...")
        
        # Parse PDF
        voters, booths = extract_voters_from_pdf(filepath)
        print(f"Parse finished. Extracted {len(voters)} voters across {len(booths)} booths.")
        
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
            if add_voter(voter['voter_id'], voter['voter_name'], voter['booth_number'], voter.get('house_number')):
                added_voters += 1
            else:
                skipped_voters += 1
        
        # Clean up uploaded file after processing
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully added {added_voters} voters (filename: {filename})',
            'added_voters': added_voters,
            'skipped_voters': skipped_voters,
            'total_booths': len(booths)
        })
    
    except Exception as e:
        print("Error processing PDF upload:")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Error processing PDF: {str(e)}'
        }), 500
    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

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
    print(f"Temporary upload folder: {app.config['UPLOAD_FOLDER']}")
    app.run(debug=debug, host='0.0.0.0', port=port)
