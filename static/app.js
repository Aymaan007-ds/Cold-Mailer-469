document.addEventListener("DOMContentLoaded", function () {
  const generateBtn = document.getElementById("generate_email_btn");
  const scheduleBtn = document.getElementById("schedule_email_btn");

  generateBtn.addEventListener("click", function () {
    // Gather data for email preview
    const data = {
      professor_name: document.getElementById("professor_name").value,
      research_title: document.getElementById("research_title").value,
      research_abstract: document.getElementById("research_abstract").value,
      student_input: document.getElementById("student_input").value,
      additional_comments: document.getElementById("additional_comments").value
    };

    fetch("/generate-email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(response => response.json())
      .then(result => {
        document.getElementById("email_preview").innerHTML = result.email_preview;
      })
      .catch(error => console.error("Error:", error));
  });

  scheduleBtn.addEventListener("click", function () {
    // Gather data for scheduling email
    const data = {
      professor_name: document.getElementById("professor_name").value,
      research_title: document.getElementById("research_title").value,
      research_abstract: document.getElementById("research_abstract").value,
      student_input: document.getElementById("student_input").value,
      additional_comments: document.getElementById("additional_comments").value,
      professor_email: document.getElementById("professor_email").value,
      timezone: document.getElementById("timezone").value,
      date: document.getElementById("date").value,
      hour: document.getElementById("hour").value,
      minute: document.getElementById("minute").value
    };

    fetch("/schedule-email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(response => response.json())
      .then(result => {
        document.getElementById("schedule_message").innerText = result.message;
      })
      .catch(error => console.error("Error:", error));
  });
});
