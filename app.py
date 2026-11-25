import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError 
import datetime
import io

# =================================================================
# FLASK APP INITIALIZATION
# =================================================================
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session management
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =================================================================
# DATABASE CONNECTION
# =================================================================
client = MongoClient("mongodb://localhost:27017/")
db = client["eye_disease_db"]
users_collection = db["users"]
scans_collection = db["scans"]
symptom_checks_collection = db["symptom_checks"]
chatbot_history_collection = db["chatbot_history"]
user_profiles_collection = db["user_profiles"]

# =================================================================
# LOAD THE PRE-TRAINED MODEL
# =================================================================
model = load_model('model/eye_disease_model.h5')
CLASS_NAMES = ['Bulging_Eyes', 'Cataracts', 'Crossed_Eyes', 'Glaucoma', 'Uveitis']

# =================================================================
# AUTHENTICATION ROUTES (LOGIN, LOGOUT, SIGNUP)
# =================================================================
@app.route('/signup', methods=['POST'])
def signup():
    """Handles new user registration."""
    if not request.is_json:
        return jsonify({"success": False, "message": "Invalid request format."}), 400
        
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    # Basic validation
    if not email or not username or not password:
        return jsonify({"success": False, "message": "Please provide email, username, and password."}), 400

    try:
        # 1. Check if user already exists
        if users_collection.find_one({"email": email}):
            return jsonify({"success": False, "message": "An account with this email already exists."})

        # 2. Register new user
        # NOTE: In a production application, you MUST hash the password here.
        new_user = {
            "email": email,
            "username": username,
            "password": password, 
            "created_at": datetime.datetime.utcnow()
        }
        result = users_collection.insert_one(new_user)
        
        # 3. Auto-login the user after successful signup
        session["user_id"] = str(result.inserted_id)
        session["username"] = username
        
        return jsonify({"success": True, "message": f"Account created! Welcome, {username}!", "username": username})
    
    except PyMongoError as e:
        print(f"MongoDB Error during signup: {e}")
        return jsonify({"success": False, "message": "A database error occurred during registration."}), 500
    except Exception as e:
        print(f"General Error during signup: {e}")
        return jsonify({"success": False, "message": "An unexpected server error occurred."}), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles root path, managing login POST requests and rendering the template."""
    # If the request is a GET request, always serve the HTML (login page if not logged in)
    if request.method == 'GET':
        return render_template('index.html', username=session.get("username"))
         
    # If the request is a POST request, it MUST be a login attempt expecting JSON response
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        try:
            user = users_collection.find_one({"email": email})
            if user:
                # Password check (In a real app, this would check a hashed password)
                if user["password"] == password:
                    # Store user's ID and username in the session
                    session["user_id"] = str(user["_id"])
                    session["username"] = user["username"]
                    return jsonify({"success": True, "message": f"Welcome, {user['username']}!", "username": user["username"]})
                else:
                    return jsonify({"success": False, "message": "Incorrect password."})
            else:
                return jsonify({"success": False, "message": f"No account found with email {email}."})
        
        except PyMongoError as e:
            print(f"MongoDB Error during login: {e}")
            return jsonify({"success": False, "message": "A database connection error occurred."}), 500
        except Exception as e:
            print(f"General Error during login: {e}")
            return jsonify({"success": False, "message": "An unexpected server error occurred."}), 500
    
    # Fallback for non-JSON POST requests or other issues
    return jsonify({"success": False, "message": "Bad Request or missing content type."}), 400

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for('index'))

# =================================================================
# CORE FEATURE: EYE SCAN PREDICTION
# =================================================================
@app.route('/predict', methods=['POST'])
def predict():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    file = request.files.get('image_file')
    if not file:
        return jsonify({"error": "No image file provided"}), 400

    try:
        # 1. Process the image for the model
        img = Image.open(file.stream).convert('RGB')
        img_resized = img.resize((224, 224))
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # 2. Make prediction
        predictions = model.predict(img_array)
        predicted_class = CLASS_NAMES[np.argmax(predictions)]
        confidence_score = float(np.max(predictions))

        # 3. Save the uploaded image file
        filename = secure_filename(f"{session['user_id']}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(image_path)
        
        # 4. Create a record for the database
        scan_record = {
            "userId": ObjectId(session["user_id"]), 
            "imageUrl": f"/static/uploads/{filename}", # URL path for the frontend
            "prediction": predicted_class,
            "confidenceScore": confidence_score,
            "scanDate": datetime.datetime.utcnow()
        }
        
        # 5. Insert the record into the 'scans' collection
        scans_collection.insert_one(scan_record)

        # 6. Return the result to the frontend
        return jsonify({
            "prediction": predicted_class,
            "confidence": f"{confidence_score:.2%}"
        })

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": "An error occurred during prediction.", "details": str(e)}), 500

# =================================================================
# DATA RETRIEVAL ROUTE FOR DASHBOARD
# =================================================================
@app.route('/dashboard_data', methods=['GET'])
def get_dashboard_data():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    user_id = ObjectId(session["user_id"])
    
    try:
        # Fetch user's scan history, sort by most recent
        scan_history = list(scans_collection.find({"userId": user_id}).sort("scanDate", -1))
        
        # Convert ObjectId to string for JSON serialization
        for scan in scan_history:
            scan["_id"] = str(scan["_id"])
            scan["userId"] = str(scan["userId"])
            
        return jsonify({"scan_history": scan_history})

    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return jsonify({"error": "Failed to load dashboard data."}), 500


# =================================================================
# PLACEHOLDER ROUTES FOR OTHER FEATURES
# =================================================================
@app.route('/symptoms', methods=['POST'])
def handle_symptoms():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    # --- Logic for symptom checker ---
    
    return jsonify({"message": "Symptom check recorded successfully."})

@app.route('/chat', methods=['POST'])
def handle_chat():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    # --- Logic for chatbot ---
    
    return jsonify({"bot_response": "This is a placeholder response from the chatbot."})

@app.route('/profile', methods=['GET', 'POST'])
def handle_profile():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401
        
    user_id = ObjectId(session["user_id"])

    if request.method == 'POST':
        # --- Logic to UPDATE profile ---
        return jsonify({"message": "Profile updated successfully."})
    
    # --- Logic to GET profile (for GET request) ---
    profile = user_profiles_collection.find_one({"userId": user_id})
    if profile:
        profile["_id"] = str(profile["_id"])
        profile["userId"] = str(profile["userId"])

    return jsonify(profile or {})


# =================================================================
# RUN THE FLASK APP
# =================================================================
if __name__ == '__main__':
    # WARNING: debug=True should only be used in development.
    app.run(debug=True)
