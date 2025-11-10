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

# using code from
# - https://github.com/theskumar/python-dotenv#readme
# - chatgpt
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from src.amigurume_api import create_app

application = create_app()
