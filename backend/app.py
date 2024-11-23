from flask import Flask, request, jsonify
from flask_cors import CORS
# import wolframalpha
from transformers import pipeline
#import openai
import os
import requests

app = Flask(__name__)
CORS(app)

# API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
API_URL_FLAN_T5 = "https://api-inference.huggingface.co/models/google/flan-t5-large"
API_KEY = "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"
API_URL_KEYPHRASE = "https://api-inference.huggingface.co/models/ml6team/keyphrase-extraction-distilbert-inspec"


pipe = pipeline("text2text-generation", model="google/flan-t5-large")

def parse(text):
    keywords = [
        "work experience", "work", "education", "skills", "skill", "experience", 
        "work history", "projects", "technical skills", "soft skills", 
        "languages", "internships", "activities"
    ]
    
    field = None  # Current section being processed
    parsed_sections = []  # List to store sections as dictionaries
    current_section_content = []  # Temporarily stores content for the current section

    # Split the text into lines
    lines = text.split("\n")

    for line in lines:
        line_lower = line.lower().strip()

        # Check if the line matches any of the keywords
        for keyword in keywords:
            if keyword in line_lower:
                # Save the current section's content if there is one
                if field and current_section_content:
                    parsed_sections.append({field: " ".join(current_section_content)})
                    current_section_content = []  # Reset the section content

                # Update the field and remove the keyword from the line
                field = keyword
                line_lower = line_lower.replace(keyword, "").strip()
                break  # Move to the next line if keyword is found

        # If a section (`field`) is active, append the cleaned line to the current section
        if field:
            if line_lower:  # Only add non-empty lines
                current_section_content.append(line_lower)

    # Add the last section to the parsed_sections list
    if field and current_section_content:
        parsed_sections.append({field: " ".join(current_section_content)})

    return parsed_sections


# text = """Work Experience
# - Software Engineer at XYZ Corp
# - Developed a machine learning model for fraud detection

# Education
# - Bachelor of Science in Computer Science

# Skills
# - Python, Machine Learning, Data Analysis

# Projects
# - Resume Feedback App: Built a web application using Flask and React"""

# parsed_sections = parse(text)
# print("Parsed Sections:")
# for section in parsed_sections:
#     print(section)



def query_huggingface_api(api_url, payload):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
        

@app.route('/analyze', methods=['POST'])
def compare():

    cv_info = request.json.get('cv')
    job_description = request.json.get('job_desc')

    if not cv_info or not job_description:
        return jsonify({"error": "Both 'cv' and 'job_desc' fields are required"}), 400

    # Step 1: Extract key phrases from job description
    job_desc_payload = {
        "inputs": job_description
    }
    job_desc_response = query_huggingface_api(API_URL_KEYPHRASE, job_desc_payload)

    job_desc_keyphrases = []
    for item in job_desc_response:
        print(item)
        if ((item['word'] != '' or item['word'] != NULL)):  # Beginning of a keyphrase
            job_desc_keyphrases.append(item['word'])
    
    # Step 2: Extract key phrases from CV
    cv_payload = {
         "inputs": cv_info
    }
    cv_response = query_huggingface_api(API_URL_KEYPHRASE, cv_payload)

    cv_keyphrases = []
    for item in cv_response:
        print(item)
        if ((item['word'] != '' or item['word'] != NULL)):  # Beginning of a keyphrase
            cv_keyphrases.append(item['word'])


    # Print the raw API response
    print("Raw API Response for CV Key Phrases:")
    print(cv_response)
   
    if "error" in cv_response:
        return jsonify({"error": cv_response["error"]}), 500
    print(cv_response)

    # Calculate missing phrases
    missing_phrases = [phrase for phrase in job_desc_keyphrases if phrase not in cv_keyphrases]


    prompt = f"""
    The resume is missing the following key phrases: {missing_phrases}. 
    Can you provide feedback on how to align the resume with the job description?  give me a paragraph.
    """


    # return jsonify({
    #     "job_desc_keyphrases": job_desc_keyphrases,
    #      "cv_keyphrases": cv_keyphrases,
    #     "missing_phrases": missing_phrases
    # }), 200 


    # prompt = f"""
    # The job description includes the following key phrases: {job_desc_keyphrases}. 
    # Compare this with the resume, which includes the following key phrases: {cv_keyphrases}. 
    # Identify which key phrases from the job description are not mentioned in the resume.
    # List these missing phrases clearly.
    # """


    flan_t5_payload = {
        "inputs": prompt,
        "parameters": {
            "num_return_sequences": 1,
            "max_length": 500,
            "temperature": 0.8,  # Adjust for more diverse responses
            "top_k": 50          # Use top_k to sample more diverse outputs
        }
    }

    flan_t5_response = query_huggingface_api(API_URL_FLAN_T5, flan_t5_payload)
    if "error" in flan_t5_response:
        return jsonify({"error": flan_t5_response["error"]}), 500

    #Extract and return the feedback
    feedback = flan_t5_response[0]["generated_text"]
    return jsonify({
        "job_desc_keyphrases": job_desc_keyphrases,
        "cv_keyphrases": cv_keyphrases,
        "feedback": feedback,
        "missing_phrases": missing_phrases
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
