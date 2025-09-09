from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from datetime import datetime
import os
import uuid
from bson import ObjectId

# Standardized upload folder path
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MongoDB Atlas connection
MONGODB_URI = 'mongodb+srv://sakshamssingh29_db_user:QTqyzm5c2gRSvosX@complaints.uyqxbrl.mongodb.net/?retryWrites=true&w=majority&appName=complaints'
client = MongoClient(MONGODB_URI)
db = client['urbanfix']
complaints_collection = db['complaints']
users_collection = db['users']

# Helper function to convert ObjectId to string for JSON serialization
def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# API Endpoints
@app.route('/complaints/submit', methods=['POST'])
def submit_complaint():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        # Handle form-data (with file upload)
        description = request.form.get('description')
        category = request.form.get('category')
        location = request.form.get('location', '')
        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename:
            ext = os.path.splitext(image_file.filename)[1]
            image_filename = f"{uuid.uuid4().hex}{ext}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        
        complaint_id = str(uuid.uuid4())[:8]
        complaint_doc = {
            'description': description,
            'complaintID': complaint_id,
            'time': datetime.utcnow().isoformat(),
            'location': location,
            'category': category,
            'image': image_filename,
            'status': 'Pending',
            'assignedDepartment': None,
            'user_id': None
        }
        result = complaints_collection.insert_one(complaint_doc)
        return jsonify({'id': str(result.inserted_id), 'complaintID': complaint_id, 'message': 'Complaint submitted successfully'}), 201
    else:
        # Handle JSON (legacy)
        data = request.get_json()
        if not data or 'description' not in data:
            abort(400, 'Description is required')
        
        complaint_id = data.get('complaintID', str(uuid.uuid4())[:8])
        complaint_doc = {
            'description': data['description'],
            'complaintID': complaint_id,
            'time': data.get('time', datetime.utcnow().isoformat()),
            'location': data.get('location', ''),
            'category': data.get('category'),
            'image': data.get('image'),
            'status': data.get('status', 'Pending'),
            'assignedDepartment': data.get('assignedDepartment'),
            'user_id': data.get('user_id')
        }
        result = complaints_collection.insert_one(complaint_doc)
        return jsonify({'id': str(result.inserted_id), 'complaintID': complaint_id, 'message': 'Complaint submitted successfully'}), 201

@app.route('/complaints/all', methods=['GET'])
def get_all_complaints():
    complaints = list(complaints_collection.find())
    result = []
    for complaint in complaints:
        result.append(serialize_doc(complaint))
    return jsonify(result)

@app.route('/complaints/<complaint_id>/status', methods=['PUT'])
def update_complaint_status(complaint_id):
    status = request.args.get('status')
    if not status:
        abort(400, 'Status is required')
    
    try:
        object_id = ObjectId(complaint_id)
        result = complaints_collection.update_one(
            {'_id': object_id},
            {'$set': {'status': status}}
        )
        if result.matched_count == 0:
            abort(404, 'Complaint not found')
        return jsonify({'id': complaint_id, 'status': status, 'message': 'Status updated successfully'})
    except Exception as e:
        abort(400, 'Invalid complaint ID')

if __name__ == '__main__':
    app.run(debug=True) 