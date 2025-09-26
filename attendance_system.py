#!/usr/bin/env python3
"""
Smart Attendance System - Main Application
Real-time face recognition and attendance marking
"""

import cv2
import numpy as np
import time
from datetime import datetime
import argparse
import sys
from face_recognition_model import FaceRecognitionModel
from database import AttendanceDatabase
from config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    CONFIDENCE_THRESHOLD, ATTENDANCE_COOLDOWN_MINUTES
)

class AttendanceSystem:
    def __init__(self):
        self.face_model = FaceRecognitionModel()
        self.db = AttendanceDatabase()
        self.last_attendance = {}  # Track last attendance time for each person
        
        # Initialize camera
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
        
        print("Smart Attendance System initialized")
        print(f"Known users: {len(self.face_model.get_known_names())}")
    
    def run(self):
        """Main loop for the attendance system"""
        print("Starting attendance system...")
        print("Press 'q' to quit, 's' to take screenshot, 'r' to reset attendance cooldown")
        
        frame_count = 0
        fps_start_time = time.time()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read from camera")
                break
            
            frame_count += 1
            
            # Process every 3rd frame for better performance
            if frame_count % 3 == 0:
                # Recognize faces
                face_locations, face_names, face_confidences = self.face_model.recognize_faces(frame)
                
                # Draw results on frame
                self.draw_results(frame, face_locations, face_names, face_confidences)
                
                # Mark attendance for recognized faces
                self.process_attendance(face_names, face_confidences)
            
            # Calculate and display FPS
            if frame_count % 30 == 0:
                fps_end_time = time.time()
                fps = 30 / (fps_end_time - fps_start_time)
                fps_start_time = fps_end_time
                
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display current time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, current_time, (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit", (frame.shape[1] - 200, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Smart Attendance System', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Screenshot saved: {filename}")
            elif key == ord('r'):
                # Reset attendance cooldown
                self.last_attendance.clear()
                print("Attendance cooldown reset")
        
        self.cleanup()
    
    def draw_results(self, frame, face_locations, face_names, face_confidences):
        """Draw face recognition results on the frame"""
        for (top, right, bottom, left), name, confidence in zip(face_locations, face_names, face_confidences):
            # Choose color based on recognition
            if name == "Unknown":
                color = (0, 0, 255)  # Red for unknown
                label = "Unknown"
            else:
                color = (0, 255, 0)  # Green for known
                label = f"{name} ({confidence:.2f})"
            
            # Draw rectangle around face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label background
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Draw label text
            cv2.putText(frame, label, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
    
    def process_attendance(self, face_names, face_confidences):
        """Process attendance for recognized faces"""
        current_time = time.time()
        
        for name, confidence in zip(face_names, face_confidences):
            if name == "Unknown" or confidence < CONFIDENCE_THRESHOLD:
                continue
            
            # Check if enough time has passed since last attendance
            if name in self.last_attendance:
                time_diff = current_time - self.last_attendance[name]
                if time_diff < (ATTENDANCE_COOLDOWN_MINUTES * 60):
                    continue  # Skip if within cooldown period
            
            # Mark attendance
            success, message = self.db.mark_attendance(name, confidence)
            
            if success:
                self.last_attendance[name] = current_time
                print(f"✅ Attendance marked for {name} (confidence: {confidence:.2f})")
            else:
                print(f"⚠️  {message} for {name}")
    
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("Attendance system stopped")

def show_statistics():
    """Show attendance statistics"""
    db = AttendanceDatabase()
    
    # Today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = db.get_attendance_by_date(today)
    
    print(f"\n=== Today's Attendance ({today}) ===")
    if today_attendance.empty:
        print("No attendance records for today")
    else:
        print(f"Total attendance: {len(today_attendance)}")
        print("\nAttendance Records:")
        for _, record in today_attendance.iterrows():
            print(f"- {record['name']} at {record['timestamp']}")
    
    # Weekly summary
    print(f"\n=== Recent Attendance Summary ===")
    summary = db.get_attendance_summary()
    if not summary.empty:
        for _, row in summary.head(7).iterrows():
            print(f"{row['date']}: {row['total_attendance']} attendees")

def main():
    parser = argparse.ArgumentParser(description='Smart Attendance System')
    parser.add_argument('--stats', action='store_true', help='Show attendance statistics')
    parser.add_argument('--camera', type=int, default=CAMERA_INDEX, help='Camera index (default: 0)')
    
    args = parser.parse_args()
    
    if args.stats:
        show_statistics()
        return
    
    try:
        # Check if any users are registered
        face_model = FaceRecognitionModel()
        if len(face_model.get_known_names()) == 0:
            print("⚠️  No users registered yet!")
            print("Please run 'python register_user.py' to register users first.")
            return
        
        # Start attendance system
        system = AttendanceSystem()
        system.run()
        
    except KeyboardInterrupt:
        print("\nSystem stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

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

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19
