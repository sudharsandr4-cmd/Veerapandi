import os

# Get the PORT from environment, default to 5000 for local development
PORT = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('FLASK_ENV') == 'development'
