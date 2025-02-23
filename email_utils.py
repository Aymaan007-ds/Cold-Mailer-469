import os
import base64
import logging
import mimetypes

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from googleapiclient.discovery import build
from authenticate import get_credentials  # Contains your OAuth2 authentication logic


# -------------------------------
# Function 1: Generate a dynamic paragraph using OpenAI's API
# -------------------------------
def generate_dynamic_paragraph(professor_name, research_title, research_paper_abstract, student_input, additional_instructions):
    # Map the student_input to a focus area
    if student_input == 1:
        focus = "Computer Vision"
    elif student_input == 2:
        focus = "Robotics"
    elif student_input == 3:
        focus = "both Computer Vision and Robotics"
    else:
        focus = "Computer Vision"  # default

    prompt = f"""
You are an AI assistant that writes professional and personalized emails to professors.

Given the professor's name and research paper abstract, compose a **single, concise paragraph** (maximum of 75 words) that highlights the student's interests in the context of the professor's work. The paragraph should begin with "Having read your work, {research_title}" and focus on {focus}. Do not include greetings or closings. Additionally, follow these instructions: {additional_instructions}
YOUR RESPONSE SHOULD BE IN PLAIN TEXT, BUT USE HTML TAGS (LIKE <br>) FOR LINE BREAKS AND (LIKE <strong>) FOR EMPHASIS. THAT IS IT. (USING AN HTML PARSER THATS WHY)
- Professor: {professor_name}
- Research Title: {research_title}
- Research Paper Abstract: {research_paper_abstract}
    """
    from openai import OpenAI
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant that composes professional emails."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    dynamic_paragraph = completion.choices[0].message.content.strip()
    return dynamic_paragraph

# -------------------------------
# Function 2: Create the HTML email message using a preset template
# -------------------------------
def create_message(professor_name, dynamic_paragraph, student_input):
    # Common introductory section
    intro_common = (
        "<p>I hope this message finds you well. My name is <strong>Narendhiran V</strong>, a third-year <strong>B.Tech student in Mechanical Engineering</strong> "
        "with a minor in <strong>Computer Science</strong> at <strong>NIT Tiruchirappalli</strong>, India.</p>"
    )

    # Insert the generated dynamic paragraph
    dynamic_section = f"<p>{dynamic_paragraph}</p>"

    # Common pre-main-body statement
    intro_common2 = (
        "<p>I’m reaching out to express my interest in a <strong>research opportunity in 2025</strong> under your guidance, "
        "along with any of your PhD scholars in the same domain.</p>"
    )

    # Main body based on student input
    if student_input == 1:  # Computer Vision
        main_body = (
            "<p><strong>Relevant Research Experience & Projects:</strong></p>"
            "<ul>"
            "<li><strong>Free Space Segmentation for COTS Robot Navigation:</strong> Co-authoring a research paper at IIT Bombay, optimizing segmentation with monocular vision and domain learning from YOLOP, restructured for real-time deployment on a Kobuki Turtlebot.</li>"
            "<li><strong>Pose and Emotion Analysis for HCI:</strong> Co-authoring another research paper on human-computer interaction and somaesthetics, analyzing dance movements and emotion of Bharatanatyam.</li>"
            "<li><strong>Autonomous Navigation in Aerial Vehicles:</strong> Created image processing and path planning systems for autonomous navigation in SAE AeroTHON-24 and MathWorks Minidrone competitions, qualifying into the top 15 teams nationwide.</li>"
            "<li><strong>Conversational Image Recognition Chatbot:</strong> Developed a multifunctional chatbot with image recognition capabilities for real-time interaction using LLaVA, SAM-2, and GLIGEN for the Smart India Hackathon Finale.</li>"
            "<li><strong>Drone-based Construction Monitoring System:</strong> Designed for Smart India Hackathon using NeRF for 3D rendering, GANs for temporal synthesis, and DeepLabV3+ for segmentation.</li>"
            "</ul>"
            "<p>I believe this background would allow me to contribute meaningfully to your research work. I would love to elaborate more on them, if required.</p>"
        )

    elif student_input == 2:  # Robotics
        main_body = (
            "<p><strong>Relevant Research Experience & Projects:</strong></p>"
            "<ul>"
            "<li><strong>Autonomous Search and Rescue Quadcopter (AeroTHON-24):</strong> Led the development of an autonomous drone for hotspot detection, integrating MAVLink and MAVProxy protocols for communication.</li>"
            "<li>Implemented <strong>SSDMobileNetV2 with an FPNLite extractor</strong> for hotspot detection and used OpenIPC for real-time digital telemetry.</li>"
            "<li>Designed and simulated in <strong>Gazebo</strong>, integrating QGroundControl SITL for flight control testing.</li>"
            "<li>Utilized <strong>Pixhawk and Raspberry Pi controllers</strong> while enhancing flight stability with a camera tilting mechanism and RTH (Return to Home) mode.</li>"
            "<li><strong>MathWorks Minidrone Competition:</strong> Led the image processing aspect for autonomous navigation using Simulink on a Parrot Mambo minidrone.</li>"
            "<li><strong>COTS Navigation Pipeline for Monocular Vision:</strong> Developed a free space segmentation model for a Kobuki bot at IIT Bombay, optimized for real-time deployment (currently in submission for 2024).</li>"
            "<li><strong>Research Papers:</strong> Co-authoring two papers—one on <strong>Pose and Emotion Analysis for HCI</strong> in Bharatanatyam and another on a <strong>Conversational Image Recognition Chatbot</strong> for Smart India Hackathon.</li>"
            "</ul>"
            "<p>I believe this background would allow me to contribute meaningfully to your research work.</p>"
        )

    elif student_input == 3:  # In Between
        main_body = (
            "<p><strong>Previous Projects & Research Experience:</strong></p>"
            "<ul>"
            "<li><strong>Free Space Segmentation for COTS Navigation with Monocular Vision:</strong> Developed at IIT Bombay for a Kobuki Turtlebot (2024 submission).</li>"
            "<li><strong>Pose and Emotion Analysis for HCI:</strong> Research paper at NIT Tiruchirappalli on Bharatanatyam movement analysis.</li>"
            "<li><strong>SAE AeroTHON-24:</strong> Built an autonomous search and rescue quadcopter; team qualified in the top 20 nationwide.</li>"
            "<li><strong>Smart India Hackathon:</strong> Developed a Conversational Image Recognition Chatbot and a DeepFake Audio-Visual Analysis Detector.</li>"
            "<li><strong>MathWorks Minidrone Competition:</strong> Led image processing for autonomous navigation in Simulink on a Parrot Mambo Minidrone at IISc, India.</li>"
            "</ul>"
            "<p>I believe this background would allow me to contribute meaningfully to your research work.</p>"
        )

    else:
        logging.error(f"Invalid student input: {student_input}")
        main_body = ""

    # Common ending section
    ending = (
        "<p>I'm aiming to advance in this field and have set my sights on higher studies, with aspirations towards a <strong>PhD</strong>. "
        "Working with you would be an invaluable step in that direction. Whether it's on-site or remote, I am open to any opportunity where I can contribute and grow under your guidance."
        "My <strong><a href='https://drive.google.com/file/d/1vasTnMajfH5YKGu1LTF4yPZn7BL2tQFk/view?usp=sharing'>Curriculum Vitae</a></strong> and <strong><a href='https://drive.google.com/file/d/1yVOolEeAEnSWA80s9pqQW5UvcR5xJ8zJ/view?usp=sharing'>Academic Transcript</a></strong> are attached for your reference.</p>"
        "<p><strong>Best regards,</strong><br>"
        "<strong>Narendhiran V</strong><br>"
        "B.Tech, <strong>Mechanical Engineering (Major)</strong> | <strong>Computer Science (Minor)</strong><br>"
        "National Institute of Technology, Tiruchirappalli<br>"
        "<strong>Phone:</strong> +91 9444749184</p>"
    )

    # Assemble the complete email body
    email_body = f"{intro_common}{dynamic_section}{intro_common2}{main_body}{ending}"
    # Prepend a greeting with the professor's name
    greeting = f"<p>Dear Professor {professor_name},</p>"
    return greeting + email_body

# -------------------------------
# Function 3: Compose the email with subject, body, and attachments
# -------------------------------
def compose_email(professor_name, dynamic_paragraph, student_input):
    subject = "Seeking Undergraduate Research Opportunity under your guidance"
    body = create_message(professor_name, dynamic_paragraph, student_input)

    if not body:
        raise ValueError("Email body could not be created due to invalid student input.")

    # Create a multipart message
    message = MIMEMultipart()
    message['subject'] = subject
    message['to'] = ""  # To be set to the professor's email when sending
    message['from'] = "me"  # Gmail API uses "me" for the authenticated user

    # Attach the HTML body
    message.attach(MIMEText(body, 'html'))

    # Attach PDF files from the 'upload' directory
    attachments = ['CV_Narendhiran.pdf', 'Transcript_Narendhiran.pdf']
    upload_dir = "uploads"

    for filename in attachments:
        filepath = os.path.join(upload_dir, filename)
        if not os.path.exists(filepath):
            logging.warning(f"Attachment {filepath} not found.")
            continue
        ctype, encoding = mimetypes.guess_type(filepath)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(filepath, "rb") as f:
            file_content = f.read()
        part = MIMEBase(maintype, subtype)
        part.set_payload(file_content)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        message.attach(part)

    return message


# -------------------------------
# Function 4: Send the email using Gmail API and authentication credentials
# -------------------------------
def send_email(message):
    creds = get_credentials()  # Retrieves credentials (authenticating if necessary)
    service = build('gmail', 'v1', credentials=creds)

    # Convert the MIME message to a base64url encoded string
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f"Email sent! Message Id: {sent_message['id']}")
    except Exception as error:
        print(f"An error occurred while sending the email: {error}")


# -------------------------------
# Example usage
# -------------------------------
if __name__ == '__main__':
    # Example professor and research details
    professor_name = "Smith"
    research_title = "Deep Learning Approaches in Computer Vision"
    research_paper_abstract = "This paper explores innovative methods in deep learning for computer vision applications."
    student_input = 3  # 1 for Computer Vision template, 2 for Robotics template, 3 for In Between template
    additional_instructions = "Use a rude tone and provide specific details about your relevant experience."

    # Generate the dynamic paragraph via OpenAI's API using the updated syntax
    dynamic_paragraph = generate_dynamic_paragraph(professor_name, research_title, research_paper_abstract, student_input, additional_instructions)
    print("Generated Dynamic Paragraph!")
    #print(dynamic_paragraph)

    # Compose the email message with attachments
    email_message = compose_email(professor_name, dynamic_paragraph, student_input)
    email_message['to'] = "aymaanalam.nitt@gmail.com"  # Replace with the actual recipient (professor's email)

    # Send the email
    send_email(email_message)
