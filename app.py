# app.py

from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import logging
import os

# Import functions from email_utils.py
from email_utils import (
    generate_dynamic_paragraph,
    compose_email,
    send_email_with_attachments
)

# Import the authenticate_gmail function from authenticate.py
from authenticate import authenticate_gmail

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/')
def index():
    # Serve the index.html file
    return send_from_directory('.', 'templates/index.html')

@app.route('/authorize')
def authorize():
    # Call authenticate_gmail function
    creds = authenticate_gmail()
    if creds:
        # Redirect back to the index page after successful authentication
        return redirect('http://localhost:5000/')
    else:
        return 'Authentication failed. Please try again.'

@app.route('/check_authentication')
def check_authentication():

    # Check if token.json exists
    if os.path.exists('token.json'):
        return jsonify({'authenticated': True})
    else:
        return jsonify({'authenticated': False})

# Route to generate email content
@app.route('/generate_email', methods=['POST'])
def generate_email_route():
    # Check if user is authenticated
    if not os.path.exists('token.json'):
        return jsonify({'error': 'User not authenticated'}), 401

    data = request.json

    # Extract data from the request
    professor_name = data.get('professor_name')
    research_title = data.get('research_title')
    research_paper_abstract = data.get('research_paper_abstract')
    student_input = int(data.get('student_input', 1))  # Default to 1 if not provided

    # Input validation
    if not all([professor_name, research_title, research_paper_abstract]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Generate the dynamic paragraph and compose email
    dynamic_paragraph = generate_dynamic_paragraph(
        professor_name, research_title, research_paper_abstract
    )
    email_body = compose_email(professor_name, dynamic_paragraph, student_input)

    # Log the generated email content
    logging.info(f"Generated email body: {email_body}")

    return jsonify({"email_body": email_body})

# Route to schedule the email
@app.route('/schedule_email', methods=['POST'])
def schedule_email():
    # Check if user is authenticated
    if not os.path.exists('token.json'):
        return jsonify({'error': 'User not authenticated'}), 401

    data = request.json

    # Extract scheduling details
    professor_email = data.get('professor_email')
    professor_timezone = data.get('professor_timezone')
    send_date = data.get('send_date')  # Expected format: 'YYYY-MM-DD'
    send_hour = data.get('send_hour')
    send_minute = data.get('send_minute')
    email_body = data.get('email_body')

    # Input validation
    if not all([professor_email, professor_timezone, send_date, send_hour, send_minute, email_body]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        send_hour = int(send_hour)
        send_minute = int(send_minute)
    except ValueError:
        return jsonify({'error': 'Invalid time format'}), 400

    # Parse and localize the send datetime
    send_datetime_str = f"{send_date} {send_hour}:{send_minute}"
    try:
        send_datetime = datetime.strptime(send_datetime_str, '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify({'error': 'Invalid date/time format'}), 400

    try:
        professor_tz = pytz.timezone(professor_timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        return jsonify({'error': 'Invalid timezone'}), 400

    send_datetime = professor_tz.localize(send_datetime)

    # Schedule the email
    job_id = f"email_{professor_email}_{int(send_datetime.timestamp())}"
    scheduler.add_job(
        func=send_email_with_attachments,
        trigger='date',
        run_date=send_datetime,
        args=[professor_email, 'Seeking Undergraduate Research Opportunity under your guidance', email_body],
        id=job_id
    )

    logging.info(f"Scheduled email to {professor_email} at {send_datetime.isoformat()} with job ID {job_id}")
    return jsonify({"message": "Email scheduled successfully!"})

if __name__ == '__main__':
    logging.info("Starting Flask server.")
    app.run(port=5000)
