// app.js

// Function to check authentication status
function checkAuthentication() {
    fetch('http://localhost:5000/check_authentication')
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
    // Redirect to Flask backend for Google OAuth (port 5000)
    window.location.href = 'http://localhost:5000/authorize';
});

// Event listener for generate and schedule button
document.getElementById('generateScheduleButton').addEventListener('click', function() {
    // Fetch data from form inputs
    const professorName = document.getElementById('professorName').value.trim();
    const researchTitle = document.getElementById('researchTitle').value.trim();
    const researchAbstract = document.getElementById('researchAbstract').value.trim();
    const professorEmail = document.getElementById('professorEmail').value.trim();
    const timezone = document.getElementById('timezone').value;
    const sendDate = document.getElementById('sendDate').value;
    const sendHour = document.getElementById('sendHour').value;
    const sendMinute = document.getElementById('sendMinute').value;
    const studentInput = document.getElementById('studentInput').value;

    // Input validation
    if (!professorName || !researchTitle || !researchAbstract || !professorEmail || !timezone || !sendDate || sendHour === '' || sendMinute === '' || !studentInput) {
        alert('Please fill in all required fields.');
        return;
    }

    // Disable the button to prevent multiple submissions
    const button = document.getElementById('generateScheduleButton');
    button.disabled = true;
    button.textContent = 'Processing...';

    // First, generate the email content
    fetch('http://localhost:5000/generate_email', {
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

        // Now schedule the email
        return fetch('http://localhost:5000/schedule_email', {
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
        });
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
        button.textContent = 'Generate and Schedule';
    })
    .catch((error) => {
        console.error('Error:', error);
        if (error.error) {
            alert('Error: ' + error.error);
        } else {
            alert('An error occurred. Please make sure you are logged in and try again.');
        }
        button.disabled = false;
        button.textContent = 'Generate and Schedule';
    });
});

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
});
