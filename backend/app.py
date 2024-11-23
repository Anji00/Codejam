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


    prompt = f"""
    The job description includes the following key phrases: {job_desc_keyphrases}.
    The resume includes the following key phrases: {cv_keyphrases}.
    Compare these and list at least 5 key phrases or skills from the job description that are missing in the resume. Provide your response as a detailed numbered list.
    """

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
        "feedback": feedback
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
