# Urbanfix - Unified Complaint Management System

## Overview
This document describes the unified complaint storage system that consolidates all previous database implementations into a single, consistent approach.

## Database Schema

### Unified Complaints Table
All complaint data is now stored in a single SQLite database at `instance/complaints.db` with the following schema:

```sql
CREATE TABLE complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    complaintID TEXT UNIQUE,
    time TEXT,
    location TEXT,
    category TEXT,
    image TEXT,
    status TEXT DEFAULT 'Pending',
    assignedDepartment TEXT,
    user_id INTEGER
);
```

### Field Descriptions
- **id**: Auto-incrementing primary key
- **description**: The complaint description (required)
- **complaintID**: Unique 8-character complaint identifier (auto-generated)
- **time**: ISO timestamp when complaint was submitted
- **location**: Location of the complaint (optional)
- **category**: Complaint category (e.g., "Road", "Water", "Electricity")
- **image**: Filename of uploaded image (stored in `static/uploads/`)
- **status**: Current status (Pending, In Progress, Resolved, etc.)
- **assignedDepartment**: Department assigned to handle the complaint
- **user_id**: ID of the user who submitted the complaint (for future user system)

## File Storage

### Image Storage
- **Path**: `static/uploads/`
- **Naming**: UUID-based filenames to prevent conflicts
- **Supported Formats**: PNG, JPG, JPEG, GIF
- **Max Size**: 16MB per file

## Components

### 1. Backend API (`backend/app.py`)
- **Database**: SQLite with SQLAlchemy ORM
- **Features**: RESTful API endpoints, user management, comprehensive complaint handling
- **Endpoints**:
  - `POST /complaints/submit` - Submit new complaint
  - `GET /complaints/all` - Get all complaints
  - `PUT /complaints/<id>/status` - Update complaint status

### 2. Automation Service (`automate/app.py`)
- **Database**: SQLite with raw SQL
- **Features**: Automated email forwarding, scheduled tasks
- **Endpoints**:
  - `POST /submit_complaint` - Submit complaint
  - `GET /get_complaints` - Retrieve complaints
  - `POST /update_status` - Update status

### 3. Main Application (`python.py`)
- **Database**: SQLite with raw SQL
- **Features**: Web interface, file upload handling, logging
- **Endpoints**:
  - `GET/POST /` - Main complaint submission form
  - `POST /submit_complaint` - API endpoint for complaint submission

## Migration

### Running the Migration Script
```bash
python migrate_database.py
```

This script will:
1. Create the new unified database schema
2. Migrate data from existing databases
3. Preserve all existing complaint data
4. Optionally clean up old database files

### Migration Process
1. **Backup existing data** (recommended)
2. **Run migration script**: `python migrate_database.py`
3. **Test all components** to ensure they work with the new schema
4. **Update any frontend code** that might reference old field names

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Werkzeug 2.3.7
- python-dotenv 1.0.0
- schedule 1.2.0

## Usage

### Starting the Backend API
```bash
cd backend
python app.py
```

### Starting the Automation Service
```bash
cd automate
python app.py
```

### Starting the Main Application
```bash
python python.py
```

## Benefits of Unified System

1. **Consistency**: All components use the same database schema
2. **Maintainability**: Single source of truth for complaint data
3. **Scalability**: Easy to add new features across all components
4. **Data Integrity**: No more data inconsistencies between components
5. **Simplified Development**: Developers only need to learn one schema

## API Compatibility

The unified system maintains backward compatibility with existing API endpoints while providing enhanced functionality through the comprehensive schema.

## Troubleshooting

### Common Issues
1. **Database not found**: Ensure `instance/` directory exists
2. **Permission errors**: Check file permissions for upload directory
3. **Migration errors**: Verify old database files are accessible

### Logs
- Main application logs: `upload.log`
- Backend logs: Console output
- Automation logs: Console output

## Future Enhancements

1. **User Authentication**: Implement user registration and login
2. **Real-time Updates**: WebSocket support for live status updates
3. **Advanced Filtering**: Search and filter complaints by various criteria
4. **Reporting**: Generate reports and analytics
5. **Mobile API**: Dedicated mobile application endpoints
