import os
from datetime import datetime

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')
ATTENDANCE_LOGS_DIR = os.path.join(BASE_DIR, 'attendance_logs')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Create directories if they don't exist
for directory in [MODELS_DIR, DATASETS_DIR, ATTENDANCE_LOGS_DIR, STATIC_DIR, TEMPLATES_DIR]:
    os.makedirs(directory, exist_ok=True)

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'attendance.db')

# Face recognition settings
FACE_RECOGNITION_TOLERANCE = 0.6
FACE_DETECTION_MODEL = 'hog'  # 'hog' or 'cnn'
MIN_FACE_SIZE = (100, 100)

# Camera settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Attendance settings
ATTENDANCE_COOLDOWN_MINUTES = 5  # Prevent duplicate entries within 5 minutes
CONFIDENCE_THRESHOLD = 0.6

# Flask settings
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
FLASK_DEBUG = True

# File paths
ENCODINGS_FILE = os.path.join(MODELS_DIR, 'face_encodings.pkl')
NAMES_FILE = os.path.join(MODELS_DIR, 'names.pkl')

# Date format
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_today_log_file():
    """Get today's attendance log file path"""
    today = datetime.now().strftime(DATE_FORMAT)
    return os.path.join(ATTENDANCE_LOGS_DIR, f'attendance_{today}.csv')

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19
