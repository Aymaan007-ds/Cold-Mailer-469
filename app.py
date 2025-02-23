import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

# Import the email generation functions from your email module
from email_utils import (
    generate_dynamic_paragraph,
    create_message,
    compose_email,
    send_email
)

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Initialize APScheduler with parallel execution enabled
executors = {
    'default': ThreadPoolExecutor(10)
}
scheduler = BackgroundScheduler(executors=executors)
scheduler.start()

logging.info("Scheduler started successfully.")


# -------------------------------
# Route: Home Page
# -------------------------------
@app.route('/')
def index():
    authenticated = os.path.exists('credentials.json')
    logging.info(f"User accessed the home page. Authenticated: {authenticated}")
    return render_template('index.html', authenticated=authenticated)


# -------------------------------
# Route: Trigger Authentication
# -------------------------------
@app.route('/authenticate')
def authenticate():
    from authenticate import get_credentials
    try:
        get_credentials()
        logging.info("OAuth authentication triggered successfully.")
    except Exception as e:
        logging.error(f"Error during authentication: {str(e)}")
    return redirect(url_for('index'))


# -------------------------------
# Route: Generate Email Preview
# -------------------------------
@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        data = request.get_json()
        professor_name = data.get('professor_name')
        research_title = data.get('research_title')
        research_abstract = data.get('research_abstract')
        student_input = int(data.get('student_input'))
        additional_comments = data.get('additional_comments', '')

        logging.info(f"Generating email preview for Professor: {professor_name}, Research Title: {research_title}")

        dynamic_paragraph = generate_dynamic_paragraph(
            professor_name, research_title, research_abstract, student_input, additional_comments
        )
        email_preview = create_message(professor_name, dynamic_paragraph, student_input)

        logging.info(f"Email preview successfully generated for {professor_name}")

        return jsonify({'email_preview': email_preview})
    except Exception as e:
        logging.error(f"Error generating email preview: {str(e)}")
        return jsonify({'error': 'Failed to generate email preview'}), 500


# -------------------------------
# Scheduled Job Function: Send Email
# -------------------------------
def scheduled_send_email(professor_name, research_title, research_abstract, student_input, additional_comments,
                         professor_email):
    try:
        logging.info(f"Scheduled email execution started for {professor_email}")

        dynamic_paragraph = generate_dynamic_paragraph(
            professor_name, research_title, research_abstract, student_input, additional_comments
        )
        email_message = compose_email(professor_name, dynamic_paragraph, student_input)
        email_message['to'] = professor_email
        send_email(email_message)

        logging.info(f"Email successfully sent to {professor_email}")
    except Exception as e:
        logging.error(f"Error in scheduled email execution for {professor_email}: {str(e)}")


# -------------------------------
# Route: Schedule Email
# -------------------------------
@app.route('/schedule-email', methods=['POST'])
def schedule_email():
    try:
        data = request.get_json()
        professor_name = data.get('professor_name')
        research_title = data.get('research_title')
        research_abstract = data.get('research_abstract')
        student_input = int(data.get('student_input'))
        additional_comments = data.get('additional_comments', '')
        professor_email = data.get('professor_email')
        timezone_str = data.get('timezone')
        date_str = data.get('date')
        hour = int(data.get('hour'))
        minute = int(data.get('minute'))

        logging.info(
            f"Received email scheduling request for {professor_email} at {date_str} {hour}:{minute} in {timezone_str} timezone.")

        local_dt = datetime.strptime(f"{date_str} {hour}:{minute}", "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(timezone_str)
        local_dt = local_tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        job = scheduler.add_job(
            scheduled_send_email,
            'date',
            run_date=utc_dt,
            args=[professor_name, research_title, research_abstract, student_input, additional_comments,
                  professor_email]
        )

        logging.info(
            f"Email successfully scheduled for {professor_email} at {utc_dt.isoformat()} UTC. Job ID: {job.id}")

        return jsonify({'message': f'Email scheduled successfully for {utc_dt.isoformat()} UTC', 'job_id': job.id})
    except Exception as e:
        logging.error(f"Error scheduling email: {str(e)}")
        return jsonify({'error': 'Failed to schedule email'}), 500


if __name__ == '__main__':
    logging.info("Flask application started.")
    app.run(debug=True)
