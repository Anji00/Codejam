from flask import Flask, request, jsonify
from flask_cors import CORS
import wolframalpha
#import openai
import os

app = Flask(__name__)
CORS(app)

app_id = '678G9G-G2438U5323'  # Replace with your Wolfram Alpha API key
client = wolframalpha.Client(app_id)
#openai.api_key = os.getenv("API_KEY")

def get_wolfram_response(query):
    try:
        result = client.query(query)
        print(f"Raw Wolfram response: {result}")
        answer = next(result.results).text
        return answer
    except StopIteration:
        return "Sorry, I couldn't find any information for that query."
    

@app.route('/analyze', methods=['POST'])
def compare():
    cv_info = request.form.get('cv')
    job_description = request.form.get('job_desc')

    prompt = f"""What kind of skills does this job need: {job_description}."""
    # prompt = f"""Use the following job description: {job_description} to provide feedback on my resume. The resume information is as follows:
    # {cv_info}. Provide actionable feedback to align the resume with the job, and keep your answer concise."""

    feedback = get_wolfram_response(prompt)
    
    return jsonify({"feedback": feedback}), 200
    

if __name__ == "__main__":
    app.run(debug=True)
