# Assuming your Flask app is named 'app.py' and is in a directory named 'app'

import sys
sys.path.insert(0, '/var/www/FlaskApp')

from app import app as application
