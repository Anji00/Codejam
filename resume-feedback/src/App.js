import React, { useState } from "react";
import axios from "axios";

function App() {
  const [resumeText, setResumeText] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [feedback, setFeedback] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append("resume_text", resumeText);
      formData.append("job_desc", jobDesc);

      const response = await axios.post("http://localhost:5000/analyze", formData);
      setFeedback(response.data.feedback);
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to get feedback. Please try again.");
    }
  };


  return (
    <div>
      <h1>Resume Feedback</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          placeholder="Paste your resume text here..."
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
        />
        <textarea
          placeholder="Paste the job description here..."
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
        />
        <button type="submit">Get Feedback</button>
      </form>
      {feedback && (
        <div>
          <h2>Feedback:</h2>
          <p>{feedback}</p>
        </div>
      )}
    </div>
  );
}

export default App;
