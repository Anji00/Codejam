import './App.css';
import React, { useState } from "react";
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';


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
    <div className="container animate__animated animate__fadeIn">

      {/* Existing Content */}
      <h1 className="display-5 fw-bold text-white">Perfect Pitch</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          className="input-box"
          placeholder="Paste your resume text here..."
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
        />
        <textarea
          className="input-box"
          placeholder="Paste the job description here..."
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
        />
        <button className="btn btn-outline-info btn-lg px-4 me-sm-3 fw-bold" type="submit">Get Feedback</button>
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
