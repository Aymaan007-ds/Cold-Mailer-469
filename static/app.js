// app.js

// Function to check authentication status
function checkAuthentication() {
    fetch('/check_authentication')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                // Hide the login button and show the form
                document.getElementById('loginButton').style.display = 'none';
                document.getElementById('formContainer').style.display = 'block';
                document.getElementById('messageArea').textContent = 'Authenticated! You can now generate and schedule emails.';
            } else {
                // Show the login button and hide the form
                document.getElementById('loginButton').style.display = 'block';
                document.getElementById('formContainer').style.display = 'none';
                document.getElementById('messageArea').textContent = 'Please log in to continue.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('messageArea').textContent = 'An error occurred while checking authentication status.';
        });
}

// Event listener for login button
document.getElementById('loginButton').addEventListener('click', function() {
    // Redirect to Flask backend for Google OAuth
    window.location.href = '/authorize';
});

// Event listener for generate email button
document.getElementById('generateEmailButton').addEventListener('click', function() {
    // Fetch data from form inputs
    const professorName = document.getElementById('professorName').value.trim();
    const researchTitle = document.getElementById('researchTitle').value.trim();
    const researchAbstract = document.getElementById('researchAbstract').value.trim();
    const studentInput = document.getElementById('studentInput').value;

    // Input validation
    if (!professorName || !researchTitle || !researchAbstract || !studentInput) {
        alert('Please fill in all required fields for generating the email.');
        return;
    }

    // Disable the button to prevent multiple submissions
    const button = document.getElementById('generateEmailButton');
    button.disabled = true;
    button.textContent = 'Generating...';

    // Generate the email content
    fetch('/generate_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            professor_name: professorName,
            research_title: researchTitle,
            research_paper_abstract: researchAbstract,
            student_input: studentInput
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => { throw data; });
        }
        return response.json();
    })
    .then(data => {
        const emailBody = data.email_body;

        // Display the generated email content
        document.getElementById('generatedEmail').value = emailBody;

        // Enable the schedule email button
        const scheduleButton = document.getElementById('scheduleEmailButton');
        scheduleButton.disabled = false;

        // Store the email body in a global variable for later use
        window.generatedEmailBody = emailBody;

        button.disabled = false;
        button.textContent = 'Generate Email';
    })
    .catch((error) => {
        console.error('Error:', error);
        if (error.error) {
            alert('Error: ' + error.error);
        } else {
            alert('An error occurred. Please try again.');
        }
        button.disabled = false;
        button.textContent = 'Generate Email';
    });
});

// Event listener for schedule email button
document.getElementById('scheduleEmailButton').addEventListener('click', function() {
    // Fetch data from form inputs
    const professorEmail = document.getElementById('professorEmail').value.trim();
    const timezone = document.getElementById('timezone').value;
    const sendDate = document.getElementById('sendDate').value;
    const sendHour = document.getElementById('sendHour').value;
    const sendMinute = document.getElementById('sendMinute').value;

    // Input validation
    if (!professorEmail || !timezone || !sendDate || sendHour === '' || sendMinute === '') {
        alert('Please fill in all required fields for scheduling the email.');
        return;
    }

    // Get the email body from the textarea (in case the user edited it)
    const emailBody = document.getElementById('generatedEmail').value.trim();

    if (!emailBody) {
        alert('Email content is empty. Please generate the email first.');
        return;
    }

    // Disable the button to prevent multiple submissions
    const button = document.getElementById('scheduleEmailButton');
    button.disabled = true;
    button.textContent = 'Scheduling...';

    // Schedule the email
    fetch('/schedule_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            professor_email: professorEmail,
            professor_timezone: timezone,
            send_date: sendDate,
            send_hour: sendHour,
            send_minute: sendMinute,
            email_body: emailBody
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => { throw data; });
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);  // Show success message
        button.disabled = false;
        button.textContent = 'Schedule Email';

        // Optionally, reset the form or disable the schedule button again
        // document.getElementById('formContainer').reset();
        // document.getElementById('scheduleEmailButton').disabled = true;
    })
    .catch((error) => {
        console.error('Error:', error);
        if (error.error) {
            alert('Error: ' + error.error);
        } else {
            alert('An error occurred. Please make sure you are logged in and try again.');
        }
        button.disabled = false;
        button.textContent = 'Schedule Email';
    });
});

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
});
