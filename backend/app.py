from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = request.form.get('resume_text')
    job_desc = request.form.get('job_desc')

    prompt = f"""
    Compare this resume:
    {resume_text}

    With this job description:
    {job_desc}

    Provide actionable feedback to align the resume with the job description.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        feedback = response['choices'][0]['message']['content']
        return jsonify({"feedback": feedback}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
