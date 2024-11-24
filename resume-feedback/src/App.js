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

      <h1 className="title">Perfect Pitch</h1>
      <form onSubmit={handleSubmit}>
      <div className="flex-container">
      <div className="rectangle">
        <textarea
          className="input-box"
          placeholder="Paste your resume text here..."
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
        />
        <div>
        <button className="clear btn btn-lg btn-outline-primary mb-3 me-sm-3 fw-bold" type="clear" >Clear All</button></div>
      </div>  
      <div></div>
      <div></div>
      <div></div>
      <div className="rectangle">
        <textarea
          className="input-box"
          placeholder="Paste the job description here..."
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
        />  
        <button className="submit btn btn-outline-info btn-lg px-4 mb-3 me-sm-3 fw-bold" type="submit">Get Feedback</button>
      </div>
      </div>        
       
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
