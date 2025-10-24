# using code from https://flask.palletsprojects.com/en/stable/deploying/mod_wsgi/
# from src.amigurume_api import create_app
# application = create_app()

# Code below copied from Google AI
import sys
import os

# Get the parent directory of the wsgi.py file
# This assumes your project structure is:
# /var/www/amigurume-api/
# ├── wsgi.py
# └── src/
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.amigurume_api import create_app

application = create_app()
