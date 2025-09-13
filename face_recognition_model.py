import cv2
import face_recognition
import pickle
import numpy as np
import os
from config import (
    ENCODINGS_FILE, NAMES_FILE, DATASETS_DIR, 
    FACE_RECOGNITION_TOLERANCE, FACE_DETECTION_MODEL,
    MIN_FACE_SIZE
)

class FaceRecognitionModel:
    def __init__(self):
        self.known_encodings = []
        self.known_names = []
        self.load_encodings()
    
    def load_encodings(self):
        """Load existing face encodings from file"""
        if os.path.exists(ENCODINGS_FILE) and os.path.exists(NAMES_FILE):
            try:
                with open(ENCODINGS_FILE, 'rb') as f:
                    self.known_encodings = pickle.load(f)
                with open(NAMES_FILE, 'rb') as f:
                    self.known_names = pickle.load(f)
                print(f"Loaded {len(self.known_names)} face encodings")
            except Exception as e:
                print(f"Error loading encodings: {e}")
                self.known_encodings = []
                self.known_names = []
        else:
            print("No existing encodings found. Starting fresh.")
    
    def save_encodings(self):
        """Save face encodings to file"""
        try:
            with open(ENCODINGS_FILE, 'wb') as f:
                pickle.dump(self.known_encodings, f)
            with open(NAMES_FILE, 'wb') as f:
                pickle.dump(self.known_names, f)
            print(f"Saved {len(self.known_names)} face encodings")
        except Exception as e:
            print(f"Error saving encodings: {e}")
    
    def add_person(self, name, image_paths):
        """Add a new person with their face images"""
        person_encodings = []
        
        for image_path in image_paths:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not load image: {image_path}")
                continue
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(rgb_image, model=FACE_DETECTION_MODEL)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) > 0:
                # Use the first face found
                person_encodings.append(face_encodings[0])
                print(f"Added encoding for {name} from {image_path}")
            else:
                print(f"No face found in {image_path}")
        
        if person_encodings:
            # Add all encodings for this person
            self.known_encodings.extend(person_encodings)
            self.known_names.extend([name] * len(person_encodings))
            self.save_encodings()
            return True
        else:
            print(f"No valid face encodings found for {name}")
            return False
    
    def recognize_faces(self, frame):
        """Recognize faces in a frame"""
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame, model=FACE_DETECTION_MODEL)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        face_names = []
        face_confidences = []
        
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_encodings, face_encoding, tolerance=FACE_RECOGNITION_TOLERANCE
            )
            name = "Unknown"
            confidence = 0.0
            
            # Calculate face distances
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_names[best_match_index]
                    # Convert distance to confidence (lower distance = higher confidence)
                    confidence = 1 - face_distances[best_match_index]
            
            face_names.append(name)
            face_confidences.append(confidence)
        
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations]
        
        return face_locations, face_names, face_confidences
    
    def remove_person(self, name):
        """Remove a person from the known faces"""
        indices_to_remove = [i for i, known_name in enumerate(self.known_names) if known_name == name]
        
        if indices_to_remove:
            # Remove in reverse order to maintain indices
            for i in reversed(indices_to_remove):
                del self.known_encodings[i]
                del self.known_names[i]
            
            self.save_encodings()
            print(f"Removed {len(indices_to_remove)} encodings for {name}")
            return True
        else:
            print(f"No encodings found for {name}")
            return False
    
    def get_known_names(self):
        """Get list of unique known names"""
        return list(set(self.known_names))
    
    def capture_face_samples(self, name, num_samples=10):
        """Capture face samples for a new person using webcam"""
        # Try different backends for camera initialization
        backends = [
            (cv2.CAP_DSHOW, 'DirectShow'),
            (cv2.CAP_MSMF, 'Media Foundation'),
            (cv2.CAP_ANY, 'Default')
        ]
        
        cap = None
        for backend, name in backends:
            try:
                cap = cv2.VideoCapture(0 + backend)
                if cap.isOpened():
                    print(f"Successfully initialized camera using {name} backend")
                    break
            except Exception as e:
                print(f"Warning: Could not initialize camera with {name} backend: {e}")
                if cap is not None:
                    cap.release()
        
        if cap is None or not cap.isOpened():
            print("Error: Could not initialize any camera backend")
            return []
            
        if not cap.isOpened():
            print("Error: Could not open camera. Please check if it's being used by another application.")
            return []
            
        # Set camera resolution (lower resolution for better performance)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        samples_captured = 0
        image_paths = []
        
        # Create person directory
        person_dir = os.path.join(DATASETS_DIR, name)
        os.makedirs(person_dir, exist_ok=True)
        
        print(f"Capturing {num_samples} samples for {name}")
        print("Make sure your face is well-lit and clearly visible")
        print("Press SPACE to capture a sample, 'q' to quit")
        
        while samples_captured < num_samples:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read from camera")
                break
                
            # Flip frame horizontally for a more intuitive mirror view
            frame = cv2.flip(frame, 1)
            
            # Display frame
            cv2.putText(frame, f"Samples: {samples_captured}/{num_samples}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press SPACE to capture, 'q' to quit", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Detect faces and draw rectangles
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            cv2.imshow('Capture Face Samples', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and len(face_locations) > 0:
                # Save the frame
                filename = f"{name}_{samples_captured + 1}.jpg"
                filepath = os.path.join(person_dir, filename)
                cv2.imwrite(filepath, frame)
                image_paths.append(filepath)
                samples_captured += 1
                print(f"Captured sample {samples_captured}")
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        return image_paths
    
    def validate_face_image(self, image_path):
        """Validate if an image contains a detectable face"""
        image = cv2.imread(image_path)
        if image is None:
            return False, "Could not load image"
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            return False, "No face detected in image"
        elif len(face_locations) > 1:
            return False, "Multiple faces detected. Please use images with single face"
        else:
            # Check face size
            top, right, bottom, left = face_locations[0]
            face_width = right - left
            face_height = bottom - top
            
            if face_width < MIN_FACE_SIZE[0] or face_height < MIN_FACE_SIZE[1]:
                return False, f"Face too small. Minimum size: {MIN_FACE_SIZE}"
            
            return True, "Valid face image"

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19
