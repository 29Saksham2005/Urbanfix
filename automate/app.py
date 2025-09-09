import os
import smtplib
import schedule
import time
from flask import Flask, request, jsonify, render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Standardized upload folder path
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB Atlas connection
MONGODB_URI = 'mongodb+srv://sakshamssingh29_db_user:QTqyzm5c2gRSvosX@complaints.uyqxbrl.mongodb.net/?retryWrites=true&w=majority&appName=complaints'
client = MongoClient(MONGODB_URI)
db = client['urbanfix']
complaints_collection = db['complaints']

# Database Initialization
def init_db():
    # MongoDB collections are created automatically when first document is inserted
    # No explicit initialization needed for MongoDB
    pass

init_db()

# 🚀 Complaint Submission API
@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    category = request.form.get("category")
    description = request.form.get("description")
    location = request.form.get("location", "")
    image = request.files.get("image")
    
    # Generate unique complaint ID
    complaint_id = str(uuid.uuid4())[:8]
    
    # Handle image upload
    image_filename = None
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        image_filename = f"{uuid.uuid4().hex}{ext}"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        image.save(image_path)

    # Insert complaint into MongoDB
    complaint_doc = {
        'description': description,
        'complaintID': complaint_id,
        'time': datetime.now().isoformat(),
        'location': location,
        'category': category,
        'image': image_filename,
        'status': 'Pending',
        'assignedDepartment': None,
        'user_id': None
    }
    complaints_collection.insert_one(complaint_doc)

    return jsonify({"message": "Complaint submitted successfully!", "complaint_id": complaint_id})

# 🚀 Retrieve Complaints API
@app.route("/get_complaints", methods=["GET"])
def get_complaints():
    complaints = list(complaints_collection.find())
    result = []
    for complaint in complaints:
        complaint['_id'] = str(complaint['_id'])  # Convert ObjectId to string
        result.append(complaint)
    return jsonify(result)

# 🚀 Update Complaint Status API
@app.route("/update_status", methods=["POST"])
def update_status():
    complaint_id = request.form.get("id")
    new_status = request.form.get("status")

    from bson import ObjectId
    try:
        object_id = ObjectId(complaint_id)
        result = complaints_collection.update_one(
            {'_id': object_id},
            {'$set': {'status': new_status}}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Complaint not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid complaint ID"}), 400

    return jsonify({"message": "Status updated successfully!"})

# 🚀 Automate Email Forwarding of Unresolved Complaints
def send_complaints():
    # Find pending complaints
    complaints = list(complaints_collection.find({"status": "Pending"}))

    if not complaints:
        print("No pending complaints to send.")
        return

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    recipient_email = os.getenv("GOVT_EMAIL")

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    for complaint in complaints:
        complaint_id = complaint['complaintID']
        category = complaint['category']
        description = complaint['description']
        
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = f"Complaint ID {complaint_id} - {category}"

        body = f"Complaint ID: {complaint_id}\nCategory: {category}\n\nDescription:\n{description}"
        msg.attach(MIMEText(body, "plain"))

        try:
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Complaint ID {complaint_id} sent successfully.")

            # Update status to 'Sent'
            complaints_collection.update_one(
                {"_id": complaint["_id"]},
                {"$set": {"status": "Sent"}}
            )

        except Exception as e:
            print(f"Failed to send Complaint ID {complaint_id}. Error: {e}")

    server.quit()

# Schedule to run every 12 hours
schedule.every(12).hours.do(send_complaints)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
