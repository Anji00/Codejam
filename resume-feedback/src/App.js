import './App.css';
import React, { useState } from "react";
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// Register the components
ChartJS.register(ArcElement, Tooltip, Legend);


function App() {
  const [resumeText, setResumeText] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [feedback, setFeedback] = useState("");
  const [similarity_list, setSimilarity] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // const formData = new FormData();
      // formData.append("cv_info", resumeText);
      // formData.append("job_desc", jobDesc);
      const data = {
        cv_info: resumeText,
        job_desc: jobDesc
      };

      const response = await axios.post("http://localhost:5001/analyze", data,
        {
          headers: {
            "Content-Type": "application/json", // Ensure the request is sent as JSON
          },
    });
      setSimilarity(response.data.similarity_list);
      setFeedback(response.data.feedback);
      console.log(similarity_list);
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to get feedback. Please try again.");
    }
  };
   // Prepare data for individual pie charts
   const chartData = similarity_list.map((item) => {
    const [category, score] = Object.entries(item)[0]; // Extract category and score
    return {
      category: category,
      data: [parseFloat((score * 100).toFixed(2)), 100 - parseFloat((score * 100).toFixed(2))], // Match percentage and remaining percentage
    };
  });

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
    },
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
        <div style={{ color: 'white' }}>
          <h2>Feedback and:</h2>
          <p>{feedback}</p>
        </div>
      )}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "20px", color: "white"}}>
        {chartData.map((item, index) => (
          <div key={index} style={{ width: "200px", margin: "20px" }}>
            <h3>{item.category}</h3>
            <Pie
              data={{
                labels: ["Similarity Score"],
                datasets: [
                  {
                    label: `${item.category} Similarity`,
                    data: item.data,
                    backgroundColor: ["#36A2EB", "#FFFFFF"]
                  },
                ],
              }}
              options={chartOptions}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
  

export default App;
