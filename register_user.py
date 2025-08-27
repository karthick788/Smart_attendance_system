#!/usr/bin/env python3
"""
User Registration Script for Smart Attendance System
Captures face samples and registers new users
"""

import sys
from face_recognition_model import FaceRecognitionModel
from database import AttendanceDatabase
import argparse

def main():
    parser = argparse.ArgumentParser(description='Register a new user for the attendance system')
    parser.add_argument('--name', type=str, help='Name of the user to register')
    parser.add_argument('--email', type=str, help='Email of the user (optional)')
    parser.add_argument('--department', type=str, help='Department of the user (optional)')
    parser.add_argument('--samples', type=int, default=10, help='Number of face samples to capture (default: 10)')
    
    args = parser.parse_args()
    
    # Initialize components
    face_model = FaceRecognitionModel()
    db = AttendanceDatabase()
    
    # Get user information
    if args.name:
        name = args.name
    else:
        name = input("Enter user name: ").strip()
    
    if not name:
        print("Error: Name cannot be empty")
        return
    
    # Check if user already exists
    existing_user = db.get_user_by_name(name)
    if existing_user:
        print(f"User '{name}' already exists in the database.")
        choice = input("Do you want to update their face data? (y/n): ").lower()
        if choice != 'y':
            return
        
        # Remove existing face encodings
        face_model.remove_person(name)
    
    email = args.email or input("Enter email (optional): ").strip() or None
    department = args.department or input("Enter department (optional): ").strip() or None
    num_samples = args.samples
    
    print(f"\nRegistering user: {name}")
    print(f"Email: {email or 'Not provided'}")
    print(f"Department: {department or 'Not provided'}")
    print(f"Face samples to capture: {num_samples}")
    print("\nMake sure you have good lighting and look directly at the camera.")
    input("Press Enter to start capturing face samples...")
    
    try:
        # Capture face samples
        image_paths = face_model.capture_face_samples(name, num_samples)
        
        if not image_paths:
            print("No face samples captured. Registration cancelled.")
            return
        
        print(f"\nCaptured {len(image_paths)} face samples")
        
        # Add person to face recognition model
        success = face_model.add_person(name, image_paths)
        
        if not success:
            print("Failed to process face samples. Registration cancelled.")
            return
        
        # Add user to database
        user_id = db.add_user(name, email, department)
        
        if user_id:
            print(f"\n✅ Successfully registered user '{name}' with ID: {user_id}")
        else:
            # User might already exist, update instead
            print(f"\n✅ Successfully updated face data for user '{name}'")
        print("Face encodings saved. User can now be recognized by the attendance system.")
        
    except KeyboardInterrupt:
        print("\nRegistration cancelled by user.")
    except Exception as e:
        print(f"\nError during registration: {e}")

def list_registered_users():
    """List all registered users"""
    db = AttendanceDatabase()
    face_model = FaceRecognitionModel()
    
    users_df = db.get_all_users()
    known_names = face_model.get_known_names()
    
    print("\n=== Registered Users ===")
    if users_df.empty:
        print("No users registered yet.")
        return
    
    print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Department':<15} {'Face Data':<10}")
    print("-" * 80)
    
    for _, user in users_df.iterrows():
        has_face_data = "Yes" if user['name'] in known_names else "No"
        email = user['email'] or 'N/A'
        department = user['department'] or 'N/A'
        
        print(f"{user['id']:<5} {user['name']:<20} {email:<25} {department:<15} {has_face_data:<10}")

def delete_user():
    """Delete a user from the system"""
    db = AttendanceDatabase()
    face_model = FaceRecognitionModel()
    
    name = input("Enter name of user to delete: ").strip()
    if not name:
        print("Name cannot be empty")
        return
    
    user = db.get_user_by_name(name)
    if not user:
        print(f"User '{name}' not found in database")
        return
    
    print(f"User found: {user[1]} (ID: {user[0]})")
    confirm = input("Are you sure you want to delete this user? (y/n): ").lower()
    
    if confirm == 'y':
        # Remove from database
        db_success = db.delete_user(name)
        
        # Remove face encodings
        face_success = face_model.remove_person(name)
        
        if db_success or face_success:
            print(f"✅ Successfully deleted user '{name}'")
        else:
            print(f"❌ Failed to delete user '{name}'")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_registered_users()
    elif len(sys.argv) > 1 and sys.argv[1] == '--delete':
        delete_user()
    else:
        main()

# Updated: 2025-12-19
