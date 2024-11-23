from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os


app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("API_KEY")


def compare():
    cv_info = request.form.get('cv')
    job_description = request.form.get('job_desc')


    prompt = f"""Use the following job description: {job_description} to provide feedback on my resume. The resume information is as follows:
    {cv_info}. Provide actionable feedback to align the resume with the job, and keep your answer concise."""

    try:
        response = openai.ChatCompletion.create(
        model = "gpt-3.5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
        )
        rcvd = response['choices'][0]['message']['content']
        return jsonify({"feedback": rcvd}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)
