# UrbanFix Python Backend

This backend is a Python Flask implementation of the UrbanFix complaint management system, migrated from Java Spring Boot.

## Features
- Submit complaints
- Retrieve all complaints
- Update complaint status

## Technology Stack
- Python 3.x
- Flask
- Flask-SQLAlchemy
- SQLite (default, can be switched to MySQL)

## Setup & Run

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the backend:
   ```sh
   python app.py
   ```
   The server will start on http://127.0.0.1:5000

## API Endpoints
- `POST /complaints/submit` — Submit a new complaint (JSON body)
- `GET /complaints/all` — Get all complaints
- `PUT /complaints/<id>/status?status=...` — Update complaint status

## Database
- By default, uses SQLite (`complaints.db`).
- To use MySQL, update the `SQLALCHEMY_DATABASE_URI` in `app.py`.

## Migration Note
- All Java and Maven files have been removed. This backend is now fully Python-based. 