import sys
import os

# Point Python path to the active FastAPI backend directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from main import app
