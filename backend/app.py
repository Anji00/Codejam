from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import requests

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


API_KEY = "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"

API_URL_SIMILARITY = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
API_URL_FLAN_T5 = "https://api-inference.huggingface.co/models/google/flan-t5-large"
API_URL_KEYPHRASE = "https://api-inference.huggingface.co/models/ml6team/keyphrase-extraction-distilbert-inspec"

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return str(e)

def parse(text):
    keywords = [
        "work experience", "work", "education", "experience", 
        "work history", "projects", "technical skills", "soft skills", 
        "skills", "skill",
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
    # text = "Jane Doe janedoe@email.com | (123) 456-7890 | LinkedIn Profile. Summary Results-oriented Project Manager with 5+ years of experience in delivering successful projects across various industries. Proven ability to lead cross-functional teams, manage complex timelines, and exceed client expectations. Seeking a challenging role to leverage my skills and contribute to organizational growth. Skills: Technical Skills: Project Management, Agile Methodologies, MS Project, Jira, Salesforce. Soft Skills: Leadership, Communication, Problem-Solving, Time Management, Negotiation. Experience: Project Manager - Acme Corporation | New York, NY | 2018-Present. Led and managed complex projects from initiation to closure, ensuring timely delivery and budget adherence. Successfully implemented a new CRM system, resulting in a 20% increase in sales efficiency. Built and mentored high-performing project teams, fostering a collaborative and innovative work environment. Project Coordinator. Global Solutions Inc. | Los Angeles, CA | 2015-2018. Coordinated and tracked project tasks, milestones, and deliverables. Prepared detailed project plans and reports, providing regular updates to stakeholders. Collaborated with cross-functional teams to ensure smooth project execution. Education: Master of Business Administration (MBA)- University of California, Los Angeles | Los Angeles, CA | 2015. Bachelor of Science in Computer Science. California State University, Long Beach | Long Beach, CA | 2013. Certifications: Project Management Professional (PMP) Certified ScrumMaster (CSM). Projects: Enterprise Resource Planning (ERP) Implementation: Led a team of 20+ to successfully implement a new ERP system, improving operational efficiency by 30%.Digital Transformation Project: Managed a cross-functional team to digitize business processes, resulting in a 25% reduction in manual tasks."
    set_parsed_sections = create_sets(parsed_sections)
    print(set_parsed_sections)
    return set_parsed_sections

def create_sets(parsed_sections):
    set_parsed_section=[]
    for item in parsed_sections:
        for key, value in item.items():
            existing_entry = next((entry for entry in set_parsed_section if key in entry), None)
            if existing_entry:
                # Append the value to the existing key, ensuring it's concatenated
                existing_entry[key] += f" {value}"
            else:
                # Add a new dictionary with the key and value
                set_parsed_section.append({key: value})
    return set_parsed_section

def query_huggingface_api(api_url, payload):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
        

@app.route('/analyze', methods=['POST'])
def compare():
    # Check if a file is uploaded
    if 'cv_file' in request.files:
        cv_file = request.files['cv_file']

        # Ensure it's a PDF file
        if cv_file.filename.split('.')[-1].lower() != 'pdf':
            return jsonify({"error": "Only PDF files are supported"}), 400

        # Extract text from the PDF
        cv_info = extract_text_from_pdf(cv_file)
        job_description = request.form.get('job_desc')
    else:
        cv_info = request.json.get('cv_info')
        job_description = request.json.get('job_desc')
    
    parsed_cv = parse(cv_info)
    if not cv_info or not job_description:
        return jsonify({"error": "Both 'cv' and 'job_desc' fields are required"}), 400

    # Step 1: Extract key phrases from job description
    job_desc_payload = {
        "inputs": job_description
    }
    job_desc_response = query_huggingface_api(API_URL_KEYPHRASE, job_desc_payload)

    job_desc_keyphrases = []
    for item in job_desc_response:
#        print("Item Type:", type(item), "Item Content:", item)
        if (item['word'] != ''):  # Beginning of a keyphrase
            job_desc_keyphrases.append(item['word'])
    
    cv_keyphrases = []
    similarity_list = []
    for x in parsed_cv:
        for key, value in x.items():
            cv_payload = {
                "inputs": value
            }
            similarity_payload = {
                "source_sentence": job_description,
                "sentences": [value]
            }
            cv_response = query_huggingface_api(API_URL_KEYPHRASE, cv_payload)

            
            similarity_response = query_huggingface_api(API_URL_SIMILARITY, similarity_payload)

            if "error" in similarity_response:
                return jsonify({"error": similarity_response["error"]}), 500
            if "error" in cv_response:
                return jsonify({"error": cv_response["error"]}), 500
            
            # to get the keyphrases from each section 
            for response in cv_response:
                if response['word'] != '':
                    cv_keyphrases.append(response['word'])

            similarity_score = similarity_response[0] 
            current_dict = {key: similarity_score}
            similarity_list.append(current_dict)
            print("Similarity score:", similarity_score)

    # calculate overall score
    similarity_payload = {
                "source_sentence": job_description,
                "sentences": [cv_info]
            }
    
    scores = [list(entry.values())[0] for entry in similarity_list]  
    average_similarity_score = sum(scores) / len(scores) if scores else 0
    similarity_list.append({"Average": average_similarity_score})

    similarity_response = query_huggingface_api(API_URL_SIMILARITY, similarity_payload)
    similarity_score = similarity_response[0] 
    similarity_list.append({"Overall": similarity_score})


    # Calculate missing phrases
    missing_phrases = [phrase for phrase in job_desc_keyphrases if phrase not in cv_keyphrases]


    prompt = f"""
    The resume is missing the following key phrases: {missing_phrases}. 
    Can you provide feedback on how to align the resume with the job description?  give me a paragraph.
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
        "feedback": feedback,
        "missing_phrases": missing_phrases,
        "similarity scores": similarity_list
    }), 200
@app.after_request
def after_request(response):
    # response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response
if __name__ == "__main__":
     app.run(debug=True, host='0.0.0.0', port=5001)