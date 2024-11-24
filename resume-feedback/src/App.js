import './App.css';
import React, { useState } from "react";
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);


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
  // Prepare data for the chart
  const chartData = {
    labels: similarity_list.map((item) => Object.keys(item)[0]), // Extract keys (categories)
    datasets: [
      {
        label: 'Similarity Percentage',
        data: similarity_list.map((item) => (Object.values(item)[0] * 100).toFixed(2)), // Convert scores to percentages
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100, // Max percentage
        title: {
          display: true,
          text: 'Percentage',
        },
      },
    },
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
        <div style={{ color: 'white' }}>
          <h2>Feedback and:</h2>
          <p>{feedback}</p>
        </div>
      )}

      {similarity_list && similarity_list.length > 0 ? (
        <div style={{ color: 'white' }}>
        <h3>Similarity Scores:</h3>
        <ul>
          {similarity_list.map((item, index) => (
            <li key={index}>
              {Object.keys(item)[0]}: {Object.values(item)[0]}
            </li>

          ))}
          <Bar data={chartData} options={chartOptions} />
        </ul>
      </div>
    ) : (
      <p>No similarity scores available</p>
    )}
    </div>
  );
}
  

export default App;
