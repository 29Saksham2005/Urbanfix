from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os
import uuid

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'  # Change to MySQL if needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    complaints = db.relationship('Complaint', backref='user', lazy=True)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    complaintID = db.Column(db.String(64), unique=True, nullable=True)
    time = db.Column(db.String(64), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(32), default='Pending')
    assignedDepartment = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

# API Endpoints
@app.route('/complaints/submit', methods=['POST'])
def submit_complaint():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        # Handle form-data (with file upload)
        description = request.form.get('description')
        category = request.form.get('category')
        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename:
            ext = os.path.splitext(image_file.filename)[1]
            image_filename = f"{uuid.uuid4().hex}{ext}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        complaint = Complaint(
            description=description,
            category=category,
            image=image_filename,
            status='Pending',
        )
        db.session.add(complaint)
        db.session.commit()
        return jsonify({'id': complaint.id, 'message': 'Complaint submitted successfully'}), 201
    else:
        # Handle JSON (legacy)
        data = request.get_json()
        if not data or 'description' not in data:
            abort(400, 'Description is required')
        complaint = Complaint(
            description=data['description'],
            complaintID=data.get('complaintID'),
            time=data.get('time', datetime.utcnow().isoformat()),
            location=data.get('location'),
            category=data.get('category'),
            image=data.get('image'),
            status=data.get('status', 'Pending'),
            assignedDepartment=data.get('assignedDepartment'),
            user_id=data.get('user_id')
        )
        db.session.add(complaint)
        db.session.commit()
        return jsonify({'id': complaint.id, 'message': 'Complaint submitted successfully'}), 201

@app.route('/complaints/all', methods=['GET'])
def get_all_complaints():
    complaints = Complaint.query.all()
    result = []
    for c in complaints:
        result.append({
            'id': c.id,
            'description': c.description,
            'complaintID': c.complaintID,
            'time': c.time,
            'location': c.location,
            'category': c.category,
            'image': c.image,
            'status': c.status,
            'assignedDepartment': c.assignedDepartment,
            'user_id': c.user_id
        })
    return jsonify(result)

@app.route('/complaints/<int:id>/status', methods=['PUT'])
def update_complaint_status(id):
    complaint = Complaint.query.get_or_404(id)
    status = request.args.get('status')
    if not status:
        abort(400, 'Status is required')
    complaint.status = status
    db.session.commit()
    return jsonify({'id': complaint.id, 'status': complaint.status, 'message': 'Status updated successfully'})

if __name__ == '__main__':
    # Ensure the database and tables are created before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True) 