# app.py
from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import hmac
import hashlib
import base64
from database import init_db, mongo
import requests
from zoom_api import get_zoom_access_token

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
@app.route("/webhook", methods=["POST"])
def zoom_webhook():
    data = request.get_json(force=True)
    print("📩 Incoming Zoom Event:", data)

    # ✅ Handle URL validation (for Server-to-Server OAuth)
    if data and data.get("event") == "endpoint.url_validation":
        plain_token = data["payload"]["plainToken"]
        client_secret = os.getenv("ZOOM_CLIENT_SECRET", "")

        # Compute encrypted token using client secret
        hash_for_validate = hmac.new(
            client_secret.encode('utf-8'),
            plain_token.encode('utf-8'),
            hashlib.sha256
        ).digest()
        encoded_hash = base64.b64encode(hash_for_validate).decode('utf-8')

        print("🔐 URL validation requested by Zoom — sending response")
        return jsonify({
            "plainToken": plain_token,
            "encryptedToken": encoded_hash
        }), 200

    # ✅ Handle normal Zoom events
    event_type = data.get("event")
    if event_type == "meeting.participant_joined":
        participant = data["payload"]["object"]["participant"]["user_name"]
        meeting_id = data["payload"]["object"]["id"]
        print(f"✅ {participant} joined meeting {meeting_id}")
    elif event_type == "meeting.participant_left":
        participant = data["payload"]["object"]["participant"]["user_name"]
        meeting_id = data["payload"]["object"]["id"]
        print(f"👋 {participant} left meeting {meeting_id}")

    return jsonify({"status": "ok"}), 200



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
