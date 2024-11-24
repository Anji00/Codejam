import './App.css';
import React, { useState } from "react";
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import applicantLogo from './applicant.png';
import paperclipIcon from './paper-clip.png';


// Register the components
ChartJS.register(ArcElement, Tooltip, Legend);


const toTitleCase = (str) => {
  return str
    .split(' ') // Split the string by spaces
    .map((word) =>
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase() // Capitalize first letter of each word
    )
    .join(' '); // Join the words back together with a space
};



function App() {
  const [cv_file, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [feedback, setFeedback] = useState("");
  const [similarity_list, setSimilarity] = useState([]);
  const [missing_phrases, setMissingPhrases] = useState([]);


  const apiClient = axios.create({
    baseURL: "http://localhost:5001"
  });
  
  // Retry logic
  apiClient.interceptors.response.use(null, async (error) => {
    const config = error.config;
    if (!config._retry) {
      config._retry = true;
      console.log("Retrying request...");
      return apiClient(config); // Retry once
    }
    return Promise.reject(error);
  });
  

  const handleClear = () => {
    // Clear both text areas by resetting their state
    setResumeText("");
    setJobDesc("");
    setFeedback("");
    setSimilarity([]);
    setMissingPhrases([]);
  };
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setResumeFile(file); // Set the selected file
    } else {
      alert("Please upload a valid PDF file.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    let response;
    try {
    if (cv_file) {
      // Handle file upload
      const formData = new FormData();
      formData.append("resume_file", cv_file);
      formData.append("job_desc", jobDesc);

      response = await apiClient.post("/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data", // ensure request is sent as form data
        },
      });
     } else if(resumeText){
    
      const data = {
        cv_info: resumeText,
        job_desc: jobDesc
      };

      response = await apiClient.post("/analyze", data,
        {
          headers: {
            "Content-Type": "application/json", // Ensure the request is sent as JSON
          },
    });
  }
      console.log("Response:", response.data);
      setSimilarity(response.data.similarity_list);
      setFeedback(response.data.feedback);
      setMissingPhrases(response.data.missing_phrases);
      
    } catch (error) {
      console.error("Request failed:", error.message);
      alert("Failed to get feedback. Please try again.");
    }
  };
   // Prepare data for individual pie charts
   const chartData = similarity_list.map((item) => {
    const [category, score] = Object.entries(item)[0]; // Extract category and score
    return {
      category: toTitleCase(category),
      data: [parseFloat((score * 100).toFixed(2)), 100 - parseFloat((score * 100).toFixed(2))], // Match percentage and remaining percentage
    };
  });

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      tooltil: {
        enabled: false,
      },
    },
    cutout: '75%',
  };

  return (
    <div className="container animate__animated animate__fadeIn">
      <div className="top">
      <img src={applicantLogo} alt="website-resume-logo"></img>
      <h1 className="title">Perfect Pitch</h1>
      </div>
      <h4>Empowering job seekers with personalized feedback, <br></br>
      This website optimizes your resume using data-driven insights to help you land your dream job!</h4>
      <form onSubmit={handleSubmit}>
      <div className="flex-container">
      <div className="rectangle">


      <div className="file-upload">
      <label htmlFor="resume-upload" className="file-label">
                <img
                  src={paperclipIcon}
                  alt="Attach Resume"
                  className="paper-clip"
                />{" "}
                Attach Resume
              </label>
              <input
                id="resume-upload"
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                style={{ display: "none" }} // Hide the default file input
              />
            </div>
            {cv_file && <p style={{ color: "white" }}>{cv_file.name}</p>}



        <textarea
          className="input-box"
          placeholder="Paste your resume text here"
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
          disabled={!!cv_file}
        />
        <div>
        <button className="clear btn btn-lg btn-outline-primary mb-3 me-sm-3 fw-bold" type="button"
                onClick={handleClear} >Clear All</button></div>
      </div>  
      <div></div>
      <div></div>
      <div></div>
      <div className="rectangle">
        <textarea
          className="input-box"
          placeholder="Paste the job description here"
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
        />  
        <button className="submit btn btn-outline-info btn-lg px-4 mb-3 me-sm-3 fw-bold" type="submit">Get Feedback</button>
      </div>
      </div>        
       
      </form>
      {feedback && (
        <div style={{ color: 'white', marginLeft:'300px', marginRight: '300px'}}>
          <h2>Feedback:</h2>
          <p>You can incorporate the following line to match the keywords
            in the job description better ajhiduegwliuqheiuhhujeiwqyiliqrui2euiew2hdliu: </p>
            <p>{feedback.replace(/[\[\]"]/g, '').trim()}</p>
        </div>
      )}
      {missing_phrases && missing_phrases.length > 0 && (
  <div style={{ color:'white', marginLeft:'300px', marginRight: '300px'}}>
    <p>
      More specifically, these are the keywords you should think about incorporating somehow into your resume to 
      better match the job description: 
    </p>

    <ul>
      <div style={{}}>
      {missing_phrases.map((phrase, index) => (
        <li key={index}>{phrase}</li>
      ))}
      </div>
    </ul>
    <div style={{}}>
    <p>Here is a detailed graphical analysis that shows how each section of your resume matches the requirements of this position: </p>
    </div>
  </div>
)}


<div className="chart-container">
  {chartData.map((item, index) => {
    const isAboveThreshold = item.data[0] > 50; // Check if the percentage is greater than 50
    const isOverall = (item.category == "Overall");
    const isAverage = (item.category == "Average");
    return (
      <div key={index} className={`chart-card ${isAboveThreshold ? 'above-50' : 'below-50'}`}>
        <div className="chart">
          <Pie
            data={{
              labels: [""],
              datasets: [
                {
                  label: ` ${item.category} Similarity `,
                  data: item.data,
                  backgroundColor: ["#36A2EB", "#EDEDED"], // Match the color scheme
                  borderWidth: 0, // No borders
                },
              ],
            }}
            options={chartOptions}
          />
          <div className="chart-center">
            <h2 style={{ color: isAboveThreshold ? 'green' : 'red' }}>
              {item.data[0]}%
            </h2>
          </div>
        </div>
        <h5 className="chart-title">{item.category}</h5>
        <div style={{color: '#000', fontSize: 'smaller'}}>
        <p>
        {isOverall ? (
          <p>
            {isAboveThreshold
              ? "Your resume looks good overall!"
              : "Consider improving your resume overall so that it matches the requirements better."}
          </p>
            ) : isAverage ? (
          <p>
            This is the average of the similarity scores for all the relevant sections in your resume.
          </p>) 
          : (
          <div> 
            <p>
              {isAboveThreshold
                ? "This section matches well with the criteria!"
                : "Consider improving this section so that it matches the requirements better."}
            </p>
          </div>
        )}

        </p>

        </div>
        </div>
      
    );
  })}
</div>
    </div>
  );
}
  

export default App;
