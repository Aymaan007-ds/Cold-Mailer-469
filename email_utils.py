# email_utils.py

import os
import base64
import mimetypes
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from openai import OpenAI  # Updated import per new syntax

# Initialize OpenAI API client
client = OpenAI(
    api_key='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'  # Replace with your actual API key
)

# Static values for attachments
ATTACHMENTS = ['CV_Narendhiran.pdf', 'Transcript_Narendhiran.pdf']
STUDENT_INTERESTS = "computer vision, robotics, and perception"

def get_gmail_service():
    """Builds the Gmail API service using credentials from token.json."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.send'])
    else:
        logging.error('token.json not found. Please run authenticate.py to generate it.')
        return None
    service = build('gmail', 'v1', credentials=creds)
    return service

def generate_dynamic_paragraph(professor_name, research_title, research_paper_abstract):
    """Generates a dynamic paragraph using OpenAI's GPT model."""
    prompt = f"""
You are an AI assistant that writes professional and personalized emails to professors.

Given the professor's name and research paper abstract, compose a **single, concise paragraph** that highlights the student's interests in the context of the professor's work.

- Professor: {professor_name}
- Research Title: {research_title}
- Research Paper Abstract: {research_paper_abstract}

Do **not** include greetings like "I hope this message finds you well" or closing statements like "Best regards". Generate only the paragraph. The student is interested in {STUDENT_INTERESTS}.
A maximum of 75 words is allowed for this paragraph. Start the concise paragraph with "Having read your work, {research_title}". Do not comment on the professor's work directly, but rather express the student's interest in it.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7
    )

    dynamic_paragraph = response.choices[0].message.content.strip()
    return dynamic_paragraph

def compose_email(professor_name, dynamic_paragraph, student_input):
    """Composes the full email body based on the student's interest area."""
    greeting = f"<p>Dear Professor {professor_name},</p>"
    intro = (
        "<p>I hope this message finds you well. "
        "My name is Narendhiran V, a third-year B.Tech student in Mechanical Engineering "
        "with a minor in Computer Science at <strong>NIT Tiruchirappalli</strong>, India.</p>"
    )

    if student_input == 1:  # Computer Vision Template
        intro += (
            f"<p>I have been following your research in <strong>Deep Learning</strong> "
            f"and <strong>Computer Vision</strong>. {dynamic_paragraph}</p>"
        )
        closing = (
            """<p>I am reaching out to express my interest in contributing to your research as a <strong>summer intern in 2025</strong> under your guidance, <strong>along with any of your PhD scholars</strong> in the same domain.<p>
                        <p>During my <strong>IIT Bombay internship</strong>, I worked on optimizing <strong>free space segmentation</strong> for <strong>COTS navigation</strong> using <strong>monocular vision</strong>. By leveraging <strong>transfer learning</strong> from <strong>YOLOP</strong>, I streamlined the model into a <strong>single-task network</strong>, replacing the SPP with a lightweight <strong>ASPP</strong>, reducing decoder heads, and integrating <strong>attention mechanisms</strong> in a <strong>pyramid fusion block</strong>. I further enhanced the architecture with a <strong>Global Feature Upsampling decoder</strong> and a <strong>Border Refinement Module</strong> to improve boundary accuracy. This model was successfully deployed for real-time navigation on a <strong>Kobuki bot</strong>, and we are currently preparing it for submission to <strong>ICRA 2025</strong>. This kind of work excites me immensely, and I see strong parallels between my interests and the work you're currently leading in <strong>Computer Vision</strong>.<p>
                        <p>In addition to my technical experience, I am co-authoring two research papers - one on <strong>Posture Recognition using EEG signals in Bharatanatyam</strong> and another on a <strong>Conversational Image Recognition Chatbot</strong>. Additionally, I have worked on the <strong>Deepfake Face-swap Detection</strong> by combining <strong>Audio-Visual Analysis</strong> and <strong>Frequency Domain Analysis</strong> for the Smart India Hackathon - these experiences have further deepened my focus on computer vision. I have also participated in competitions like <strong>SAE AeroTHON-24</strong> and the <strong>MathWorks Minidrone Competition</strong>, where I developed <strong>image processing systems</strong> for <strong>autonomous navigation tasks</strong> in aerial vehicles. I believe this background would allow me to contribute meaningfully to your research work.<p>
                        <p>I am aiming to advance in this field and have set my sights on <strong>higher studies</strong>, with aspirations towards a <strong>PhD</strong>. Working with you would be an invaluable step in that direction. Whether it's on-site or remote, I am open to any opportunity where I can contribute and grow under your guidance. My <strong><a href="https://drive.google.com/file/d/1vasTnMajfH5YKGu1LTF4yPZn7BL2tQFk/view?usp=sharing">Curriculum Vitae</a></strong> and <strong><a href="https://drive.google.com/file/d/1yVOolEeAEnSWA80s9pqQW5UvcR5xJ8zJ/view?usp=sharing">Academic Transcript</a></strong> are attached for your reference. I would be happy to discuss how I can contribute to your research.<p>
"""
        )
    elif student_input == 2:  # Robotics Template
        intro += (
            f"<p>I have been following your research in <strong>Computer Vision</strong> "
            f"and <strong>Robotics</strong>. {dynamic_paragraph}</p>"
        )
        closing = (
            """<p>I am reaching out to express my interest in contributing to your research as a <strong>summer intern in 2025</strong> under your guidance, <strong>along with any of your PhD scholars</strong> in the same domain.<p>
                                <p>As part of the <strong>AeroTHON-24 competition</strong>, I led the development of an <strong>autonomous search and rescue quadcopter</strong>. The drone autonomously detected and classified <strong>hotspots</strong> using <strong>MAVLink</strong> and <strong>MAVProxy</strong> protocols for communication. I implemented <strong>SSDMobileNetV2</strong> with a <strong>FPNLite extractor</strong> for hotspot detection, along with <strong>OpenIPC</strong> for real-time digital telemetry. I also contributed to the design and simulation in <strong>Gazebo</strong>, integrating <strong>QGroundControl SITL</strong> for flight control testing. We used <strong>Pixhawk</strong> and <strong>Raspberry Pi</strong> controllers, and enhanced flight stability with a <strong>camera tilting mechanism</strong> and </strong>RTH (Return to Home) mode</strong> for safety. This kind of work excites me immensely, and I see strong parallels between my interests and the work you're currently leading.<p>
                                <p>Additionally, I participated in the <strong>MathWorks Minidrone Competition</strong>, where I led the <strong>image processing aspect for autonomous navigation</strong> using <strong>Simulink</strong> on a <strong>Parrot Mambo minidrone</strong>. During my <strong>IIT Bombay internship</strong>, I developed a <strong>COTS navigation pipeline</strong> for <strong>monocular vision</strong> on a <strong>Kobuki bot</strong>, optimizing <strong>real-time free space segmentation</strong> for autonomous navigation, which is submitted to <strong>ICRA 2025</strong>.<p>
                                <p>Beyond these competitions, I am also co-authoring two research papers - one on <strong>Posture Recognition using EEG signals in Bharatanatyam</strong> and another on a <strong>Conversational Image Recognition Chatbot</strong> for the <strong>Smart India Hackathon</strong> - both of which have further deepened my focus on <strong>computer vision</strong>. I believe this background would allow me to contribute meaningfully to your research work.<p>
                                <p>I am aiming to advance in this field and have set my sights on <strong>higher studies</strong>, with aspirations towards a <strong>PhD</strong>. Working with you would be an invaluable step in that direction. Whether it's on-site or remote, I am open to any opportunity where I can contribute and grow under your guidance. My <strong><a href="https://drive.google.com/file/d/1vasTnMajfH5YKGu1LTF4yPZn7BL2tQFk/view?usp=sharing">Curriculum Vitae</a></strong> and <strong><a href="https://drive.google.com/file/d/1yVOolEeAEnSWA80s9pqQW5UvcR5xJ8zJ/view?usp=sharing">Academic Transcript</a></strong> are attached for your reference. I would be happy to discuss how I can contribute to your research.<p>
                """
        )
    signature = (
        "<p>Best regards,<br>"
        "Narendhiran V<br>"
        "B.Tech, Mechanical Engineering (Major) | Computer Science (Minor)<br>"
        "National Institute of Technology, Tiruchirappalli<br>"
        "Phone: +91 9444749184</p>"
    )

    email_body = f"{greeting}{intro}{closing}{signature}"
    return email_body

def create_message_with_attachments(sender, to, subject, body_html, attachments):
    """Creates an email message with attachments."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Attach the HTML body
    msg = MIMEText(body_html, 'html')
    message.attach(msg)

    # Attach files
    for file_path in attachments:
        if not os.path.exists(file_path):
            logging.error(f"Attachment not found: {file_path}")
            continue

        content_type, encoding = mimetypes.guess_type(file_path)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        main_type, sub_type = content_type.split('/', 1)
        with open(file_path, 'rb') as file:
            file_data = MIMEBase(main_type, sub_type)
            file_data.set_payload(file.read())
            encoders.encode_base64(file_data)
            file_data.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(file_path)}"'
            )
            message.attach(file_data)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email_with_attachments(to_email, subject, body_html):
    """Sends an email with attachments using the Gmail API."""
    service = get_gmail_service()
    if service is None:
        logging.error('Failed to get Gmail service.')
        return

    # Retrieve the sender's email address using the Gmail API
    try:
        profile = service.users().getProfile(userId='me').execute()
        sender_email = profile['emailAddress']
    except Exception as error:
        logging.error(f"An error occurred while retrieving sender's email: {error}")
        sender_email = 'me'  # Default to 'me' if unable to get the email address

    message = create_message_with_attachments(
        sender=sender_email,
        to=to_email,
        subject=subject,
        body_html=body_html,
        attachments=ATTACHMENTS
    )

    try:
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        logging.info(f"Email sent to {to_email} with message ID: {sent_message['id']}")
    except Exception as error:
        logging.error(f"An error occurred while sending email to {to_email}: {error}")
