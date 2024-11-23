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
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
API_KEY = "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"


# app_id = '678G9G-5EK22HVP4T'  # conversational
# client = wolframalpha.Client(app_id)

#openai.api_key = os.getenv("API_KEY")

pipe = pipeline("text2text-generation", model="google/flan-t5-large")


def query_huggingface_api(payload):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

# def get_wolfram_response(query):
#     try:
#         result = client.query(query)
#         print(f"Raw Wolfram response: {result}")
#         answer = next(result.results).text
#         return answer
#     except StopIteration:
#         return "Sorry, I couldn't find any information for that query."
    

@app.route('/analyze', methods=['POST'])
def compare():


    cv_info = request.json.get('cv')
    job_description = request.json.get('job_desc')

    if not cv_info or not job_description:
        return jsonify({"error": "Both 'cv' and 'job_desc' fields are required"}), 400
    
    # number = request.json.get('number')
    # prompt = f"""What is 2 + {number}?"""
    # prompt = f"""can you help me find a car?"""

    prompt = f"""
    Based on the following job description: 
    {job_description}

    Compare it to my resume information:
    {cv_info}

    Identify and list at least 5 skills, qualifications, or experiences mentioned in the job description but missing from my CV. Provide your response as a detailed numbered list.
    """

    try:
        payload = {
            "inputs": prompt, 
            "parameters": { 
                "num_return_sequences": 1,
                "max_length": 500,
                "temperature": 0.8,  # Adjust for more diverse responses
                "top_k": 50  # Use top_k to sample more diverse outputs
                }
            
            }
    #     payload = {
    #     "inputs": {
    #         "source_sentence": job_description,
    #         "sentences": [cv_info]
    #     }
    # }
        response = query_huggingface_api(payload)

        # Check for errors in the API response
        if "error" in response:
            return jsonify({"error": response["error"]}), 500

        # Extract and return the generated text
        feedback = response[0]["generated_text"]

    #     score = response[0]  # The first similarity score
    #     feedback = {
    #     "similarity_score": score,
    #     "message": "High alignment!" if score > 0.75 else "Moderate or low alignment. Consider updating your resume to better match the job description."
    # }

        return jsonify({"feedback": feedback}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

if __name__ == "__main__":
    app.run(debug=True)
