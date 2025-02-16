import os
import sqlite3
import smtplib
import schedule
import time
from flask import Flask, request, jsonify, render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_FILE = "complaints.db"

# Database Initialization
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            description TEXT,
            image_path TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 🚀 Complaint Submission API
@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    category = request.form.get("category")
    description = request.form.get("description")
    image = request.files.get("image")

    if image:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
        image.save(image_path)
    else:
        image_path = None

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO complaints (category, description, image_path) VALUES (?, ?, ?)",
                   (category, description, image_path))
    conn.commit()
    conn.close()

    return jsonify({"message": "Complaint submitted successfully!"})

# 🚀 Retrieve Complaints API
@app.route("/get_complaints", methods=["GET"])
def get_complaints():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    conn.close()

    return jsonify([{"id": c[0], "category": c[1], "description": c[2], "image": c[3], "status": c[4]} for c in complaints])

# 🚀 Update Complaint Status API
@app.route("/update_status", methods=["POST"])
def update_status():
    complaint_id = request.form.get("id")
    new_status = request.form.get("status")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Status updated successfully!"})

# 🚀 Automate Email Forwarding of Unresolved Complaints
def send_complaints():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, description FROM complaints WHERE status='Pending'")
    complaints = cursor.fetchall()
    conn.close()

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
        complaint_id, category, description = complaint
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = f"Complaint ID {complaint_id} - {category}"

        body = f"Complaint ID: {complaint_id}\nCategory: {category}\n\nDescription:\n{description}"
        msg.attach(MIMEText(body, "plain"))

        try:
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Complaint ID {complaint_id} sent successfully.")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE complaints SET status='Sent' WHERE id=?", (complaint_id,))
            conn.commit()
            conn.close()

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
