#!/usr/bin/env python3
"""
Flask Web Dashboard for Smart Attendance System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from database import AttendanceDatabase
from face_recognition_model import FaceRecognitionModel
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, TEMPLATES_DIR, STATIC_DIR

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.secret_key = 'smart_attendance_system_2024'

# Initialize components
db = AttendanceDatabase()
face_model = FaceRecognitionModel()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    # Get today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = db.get_attendance_by_date(today)
    
    # Get recent attendance summary
    summary = db.get_attendance_summary()
    
    # Get all registered users
    users = db.get_all_users()
    known_names = face_model.get_known_names()
    
    # Calculate statistics
    stats = {
        'total_users': len(users),
        'today_attendance': len(today_attendance),
        'users_with_face_data': len(known_names),
        'total_days_recorded': len(summary)
    }
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         today_attendance=today_attendance.to_dict('records'),
                         summary=summary.head(7).to_dict('records'),
                         current_date=today)

@app.route('/users')
def users():
    """Users management page"""
    users_df = db.get_all_users()
    known_names = face_model.get_known_names()
    
    # Add face data status to users
    users_list = []
    for _, user in users_df.iterrows():
        user_dict = user.to_dict()
        user_dict['has_face_data'] = user['name'] in known_names
        users_list.append(user_dict)
    
    return render_template('users.html', users=users_list)

@app.route('/attendance')
def attendance():
    """Attendance records page"""
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get attendance summary
    summary = db.get_attendance_summary(start_date, end_date)
    
    return render_template('attendance.html', 
                         summary=summary.to_dict('records'),
                         start_date=start_date,
                         end_date=end_date)

@app.route('/attendance/<date>')
def attendance_detail(date):
    """Detailed attendance for a specific date"""
    try:
        datetime.strptime(date, '%Y-%m-%d')  # Validate date format
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('attendance'))
    
    attendance_records = db.get_attendance_by_date(date)
    
    return render_template('attendance_detail.html', 
                         records=attendance_records.to_dict('records'),
                         date=date)

@app.route('/api/attendance/today')
def api_today_attendance():
    """API endpoint for today's attendance"""
    today = datetime.now().strftime('%Y-%m-%d')
    attendance = db.get_attendance_by_date(today)
    
    return jsonify({
        'date': today,
        'count': len(attendance),
        'records': attendance.to_dict('records')
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = db.get_attendance_by_date(today)
    users = db.get_all_users()
    known_names = face_model.get_known_names()
    summary = db.get_attendance_summary()
    
    return jsonify({
        'total_users': len(users),
        'today_attendance': len(today_attendance),
        'users_with_face_data': len(known_names),
        'total_days_recorded': len(summary)
    })

@app.route('/api/attendance/chart')
def api_attendance_chart():
    """API endpoint for attendance chart data"""
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    
    summary = db.get_attendance_summary(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Fill missing dates with 0
    chart_data = []
    for i in range(days):
        current_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        count = 0
        
        for _, row in summary.iterrows():
            if row['date'] == current_date:
                count = row['total_attendance']
                break
        
        chart_data.append({
            'date': current_date,
            'count': count
        })
    
    return jsonify(chart_data)

@app.route('/delete_user/<name>', methods=['POST'])
def delete_user(name):
    """Delete a user"""
    try:
        # Remove from database
        db_success = db.delete_user(name)
        
        # Remove face encodings
        face_success = face_model.remove_person(name)
        
        if db_success or face_success:
            flash(f'Successfully deleted user: {name}', 'success')
        else:
            flash(f'User not found: {name}', 'error')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('users'))

@app.route('/export/<date>')
def export_attendance(date):
    """Export attendance for a specific date as CSV"""
    try:
        datetime.strptime(date, '%Y-%m-%d')  # Validate date format
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('attendance'))
    
    attendance_records = db.get_attendance_by_date(date)
    
    if attendance_records.empty:
        flash(f'No attendance records found for {date}', 'warning')
        return redirect(url_for('attendance'))
    
    # Create CSV response
    from flask import Response
    import io
    
    output = io.StringIO()
    attendance_records.to_csv(output, index=False)
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attendance_{date}.csv'}
    )

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

if __name__ == '__main__':
    print(f"Starting Smart Attendance Dashboard...")
    print(f"Access the dashboard at: http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19
