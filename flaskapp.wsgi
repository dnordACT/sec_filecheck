import sys
import site

python_version = 'python3.11.2'
# Add the site-packages of your virtual environment
site.addsitedir(f'/var/www/sec_filecheck/app/venv/lib/{python_version}/site-packages')

sys.path.insert(0, '/var/www/sec_filecheck/app')

from app import app as application