from flask import Flask, request, render_template_string, jsonify, session
import openai
import requests
import json
import base64
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.secret_key = 'replace-with-your-secret-key'

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/oz6cgrhqg8bctxvqhscaws053nery1mp"

@app.route('/', methods=['GET'])
def index():
    return render_template_string("""
    <!doctype html>
    <title>Business Card OCR</title>
    <h1>Upload a Business Card Image</h1>
    <form method=post enctype=multipart/form-data action="/extract">
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """)

@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    image_data = base64.b64encode(file.read()).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    prompt = """
You are given an image of a business card. Extract the following details as JSON:
{
  "full_name": "",
  "first_name": "",
  "last_name": "",
  "email": "",
  "handphone_number": "",
  "job_title": "",
  "company_name": "",
  "company_website": "",
  "city": "",
  "country": ""
}
Make sure all fields are strings, even if empty.
"""

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }}
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code != 200:
        return jsonify({"error": "OpenAI API request failed", "details": response.text})

    result = response.json()
    try:
        text_output = result["choices"][0]["message"]["content"]
        json_data = json.loads(text_output)
    except Exception as e:
        return jsonify({"error": "Failed to parse OpenAI response", "details": str(e)})

    # Fix phone formatting issue
    if json_data.get("handphone_number", "").startswith("+"):
        json_data["handphone_number"] = "'" + json_data["handphone_number"]

    json_data["timestamp"] = datetime.now().isoformat()

    webhook_response = requests.post(
        MAKE_WEBHOOK_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(json_data)
    )

    return jsonify({
        "openai_response": json_data,
        "webhook_status": webhook_response.status_code
    })

if __name__ == '__main__':
    app.run(debug=True)
