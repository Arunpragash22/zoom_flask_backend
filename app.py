# app.py
from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from database import init_db, mongo
import requests
from zoom_api import get_zoom_access_token
from pyngrok import ngrok
from flask import request


# Load .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure MongoDB
app.config["MONGO_URI"] = "mongodb+srv://vimalanarunpragash2000_db_user:MyMongo123@cluster0.p7avgza.mongodb.net/zoomproject?retryWrites=true&w=majority&appName=Cluster0"

init_db(app)

# Test route
@app.route('/')
def home():
    return jsonify({"message": "Flask + MongoDB connected successfully!"})

# Add data route
@app.route('/add')
def add_data():
    mongo.db.students.insert_one({"name": "Arun", "project": "Zoom Integration"})
    return jsonify({"status": "success", "message": "Data added to MongoDB"})

# Get data route
@app.route('/get')
def get_data():
    data = list(mongo.db.students.find({}, {"_id": 0}))
    return jsonify(data)

# ✅ Create Zoom Meeting route
@app.route('/create_meeting')
def create_meeting():
    access_token = get_zoom_access_token()
    url = "https://api.zoom.us/v2/users/me/meetings"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "topic": "Test Meeting by Tivinstan",
        "type": 1,  # Instant meeting
        "settings": {
            "join_before_host": True,
            "approval_type": 0,
            "registration_type": 1
        }
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
   
    # Save meeting info in MongoDB
    mongo.db.meetings.insert_one(result)

    return jsonify({
        "status": "created",
        "meeting_id": result.get("id"),
        "join_url": result.get("join_url")
    })

# Webhook endpoint for Zoom events
@app.route('/webhook', methods=['GET', 'POST'])
def zoom_webhook():
    # Handle POST events from Zoom
    if request.method == "POST":
        data = request.json
        print("Received Zoom webhook:", data)

    # Always respond 200 OK for GET or POST
    return jsonify({"status": "ok"}), 200



# ✅ Keep this last
if __name__ == '__main__':
     # Start Ngrok tunnel
     #public_url = ngrok.connect(int(os.getenv("PORT", 5000)))
     #print("Ngrok tunnel URL:", public_url)
     #print("Webhook endpoint:", f"{public_url}/webhook")
    
     app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
