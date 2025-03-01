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
        access_token = create_access_token(identity=str(user.id))  # ✅ Ensure identity is a string
        return jsonify(access_token=access_token)
    return jsonify({"error": "Invalid credentials"}), 401

from datetime import datetime

@app.route('/submit_timesheet', methods=['POST'])
@jwt_required()
def submit_timesheet():
    try:
        data = request.json
        print("Received Data:", data)  # Debugging

        if not data:
            return jsonify({"error": "No data received"}), 400

        user_id = get_jwt_identity()
        print(f"User ID: {user_id}")  # Debugging

        # Validate all required fields
        required_fields = ["project_name", "project_cost_number", "worker_name", "date", "job_description"]
        for field in required_fields:
            if field not in data or not data[field]:
                print(f"Missing field: {field}")  # Debugging
                return jsonify({"error": f"Missing required field: {field}"}), 422

        # Convert date string to Python date object
        try:
            date_obj = datetime.strptime(data["date"], "%Y-%m-%d").date()  # ✅ Convert string to date
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 422

        # Save timesheet to database
        new_timesheet = Timesheet(
            project_name=data["project_name"],
            project_cost_number=data["project_cost_number"],
            worker_name=data["worker_name"],
            date=date_obj,  # ✅ Now using correct date format
            job_description=data["job_description"],
            signature_1=data.get("signature_1", None),
            user_id=user_id
        )

        db.session.add(new_timesheet)
        db.session.commit()

        return jsonify({"message": "Timesheet submitted successfully"}), 201

    except Exception as e:
        print(f"Error submitting timesheet: {str(e)}")  # Debugging
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

from flask_jwt_extended import jwt_required, get_jwt_identity

from flask import Response, send_file
from fpdf import FPDF
import os

@app.route('/generate_pdf/<int:timesheet_id>', methods=['GET'])
@jwt_required()
def generate_pdf(timesheet_id):
    user_id = get_jwt_identity()
    timesheet = Timesheet.query.filter_by(id=timesheet_id, user_id=user_id).first()

    if not timesheet:
        return jsonify({"error": "Timesheet not found or unauthorized"}), 403

    try:
        # ✅ Generate PDF File
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Timesheet Report", ln=True, align="C")

        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Project: {timesheet.project_name}", ln=True)
        pdf.cell(200, 10, txt=f"Cost Number: {timesheet.project_cost_number}", ln=True)
        pdf.cell(200, 10, txt=f"Worker: {timesheet.worker_name}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {timesheet.date}", ln=True)
        pdf.multi_cell(0, 10, txt=f"Job Description: {timesheet.job_description}")

        # ✅ Save the PDF to a temporary file
        pdf_filename = f"timesheet_{timesheet_id}.pdf"
        pdf_path = os.path.join("/tmp", pdf_filename)
        pdf.output(pdf_path)

        # ✅ Send the PDF file to the user
        return send_file(pdf_path, as_attachment=True, mimetype="application/pdf")

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"username": user.username}), 200

@app.route('/delete_timesheet/<int:timesheet_id>', methods=['DELETE'])
@jwt_required()
def delete_timesheet(timesheet_id):
    try:
        user_id = get_jwt_identity()
        timesheet = Timesheet.query.filter_by(id=timesheet_id, user_id=user_id).first()

        if not timesheet:
            return jsonify({"error": "Timesheet not found or unauthorized"}), 403

        db.session.delete(timesheet)
        db.session.commit()

        return jsonify({"message": "Timesheet deleted successfully"}), 200

    except Exception as e:
        print(f"Error deleting timesheet: {str(e)}")  # Debugging
        return jsonify({"error": str(e)}), 500