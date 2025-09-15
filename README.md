# Smart Attendance System

A real-time facial recognition-based attendance system that automates attendance marking with high accuracy and minimal manual intervention.

## Features

- **Real-time Face Detection**: Live webcam feed processing using OpenCV
- **Facial Recognition**: Deep learning-based face recognition with high accuracy
- **Automated Attendance Logging**: Timestamp-based attendance records with duplicate prevention
- **Web Dashboard**: Flask-based interface for viewing attendance records and managing users
- **Data Export**: CSV and database export capabilities
- **User Management**: Add, remove, and manage registered users

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Register New Users
```bash
python register_user.py
```

### 2. Start Attendance System
```bash
python attendance_system.py
```

### 3. View Dashboard
```bash
python app.py
```
Then open http://localhost:5000 in your browser

## Project Structure

```
smart-attendance-system/
├── app.py                 # Flask web application
├── attendance_system.py   # Main attendance system
├── register_user.py       # User registration script
├── face_recognition_model.py  # Face recognition utilities
├── database.py           # Database operations
├── config.py             # Configuration settings
├── models/               # Trained models storage
├── datasets/             # User face datasets
├── attendance_logs/      # Attendance CSV files
├── static/               # Web assets
├── templates/            # HTML templates
└── requirements.txt      # Python dependencies
```

## Technologies Used

- **Python**: Core programming language
- **OpenCV**: Computer vision and image processing
- **face_recognition**: Facial recognition library
- **Flask**: Web framework for dashboard
- **SQLite**: Local database for attendance records
- **scikit-learn**: Machine learning utilities
- **NumPy & Pandas**: Data processing

## License

MIT License

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->

<!-- Updated: 2025-12-19 -->
