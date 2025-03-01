from flask import request, jsonify
from app import app, db
from models import User, Timesheet
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/submit_timesheet', methods=['POST'])
@jwt_required()
def submit_timesheet():
    try:
        data = request.json
        print("Received Data:", data)

        if not data:
            return jsonify({"error": "No data received"}), 400

        user_id = get_jwt_identity()

        required_fields = ["project_name", "project_cost_number", "worker_name", "date", "job_description"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 422

        new_timesheet = Timesheet(
            project_name=data["project_name"],
            project_cost_number=data["project_cost_number"],
            worker_name=data["worker_name"],
            date=data["date"],
            job_description=data["job_description"],
            signature_1=data.get("signature_1", None),
            user_id=user_id
        )

        db.session.add(new_timesheet)
        db.session.commit()

        return jsonify({"message": "Timesheet submitted successfully"}), 201

    except Exception as e:
        print(f"Error submitting timesheet: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/timesheets', methods=['GET'])
@jwt_required()
def get_timesheets():
    try:
        user_id = get_jwt_identity()
        timesheets = Timesheet.query.filter_by(user_id=user_id).all()

        if not timesheets:
            return jsonify([]), 200

        return jsonify([{
            "id": ts.id,
            "project_name": ts.project_name,
            "project_cost_number": ts.project_cost_number,
            "worker_name": ts.worker_name,
            "date": str(ts.date),
            "job_description": ts.job_description
        } for ts in timesheets]), 200

    except Exception as e:
        print(f"Error fetching timesheets: {str(e)}")
        return jsonify({"error": str(e)}), 500

## Generating PDF Files

from reportlab.pdfgen import canvas
import io

@app.route('/generate_pdf/<int:timesheet_id>', methods=['GET'])
@jwt_required()
def generate_pdf(timesheet_id):
    timesheet = Timesheet.query.get_or_404(timesheet_id)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, f"Project: {timesheet.project_name}")
    pdf.drawString(100, 730, f"Cost Number: {timesheet.project_cost_number}")
    pdf.drawString(100, 710, f"Worker: {timesheet.worker_name}")
    pdf.drawString(100, 690, f"Date: {timesheet.date}")
    pdf.drawString(100, 670, f"Job Description: {timesheet.job_description}")

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue(), 200, {'Content-Type': 'application/pdf'}
