from flask import Flask, request, render_template_string, jsonify, session
import openai
import requests
import json
import base64
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration - Set your OpenAI API key here
OPENAI_API_KEY = "your-openai-api-key-here"
ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/placeholder/test"

openai.api_key = OPENAI_API_KEY

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Card Extractor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .upload-area { 
            border: 3px dashed #007bff; 
            border-radius: 10px; 
            padding: 40px; 
            text-align: center; 
            background: rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }
        .upload-area:hover { background: rgba(255,255,255,0.2); }
        .preview-img { max-width: 100%; max-height: 300px; border-radius: 10px; }
        .field-group { margin-bottom: 15px; }
        .btn-custom { border-radius: 25px; padding: 10px 30px; }
        .spinner-border-sm { width: 1rem; height: 1rem; }
    </style>
</head>
<body>
    <div class="container py-4">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header bg-primary text-white text-center">
                        <h3><i class="bi bi-card-text"></i> Business Card Extractor</h3>
                        <small>Upload your business card and extract contact information instantly</small>
                    </div>
                    <div class="card-body">
                        {% if step == 'upload' %}
                        <form id="uploadForm" enctype="multipart/form-data">
                            <div class="upload-area" onclick="document.getElementById('imageInput').click()">
                                <input type="file" id="imageInput" name="image" accept="image/*" style="display: none;" onchange="previewImage(this)">
                                <div id="uploadContent">
                                    <i class="bi bi-cloud-upload" style="font-size: 3rem; color: #007bff;"></i>
                                    <h5>Click to upload business card</h5>
                                    <p class="text-muted">JPG, PNG supported • Best with good lighting</p>
                                </div>
                                <div id="imagePreview" style="display: none;">
                                    <img id="previewImg" class="preview-img" alt="Preview">
                                    <p class="mt-2"><small class="text-success">Image ready for processing</small></p>
                                </div>
                            </div>
                            <div class="text-center mt-4">
                                <button type="submit" class="btn btn-primary btn-custom" id="processBtn" disabled>
                                    <span id="btnText">Process Business Card</span>
                                    <span id="btnSpinner" class="spinner-border spinner-border-sm ms-2" style="display: none;"></span>
                                </button>
                            </div>
                        </form>

                        {% elif step == 'confirm' %}
                        <div class="row">
                            <div class="col-md-4">
                                <img src="data:image/jpeg;base64,{{ image_data }}" class="preview-img" alt="Business Card">
                            </div>
                            <div class="col-md-8">
                                <h5>Extracted Information</h5>
                                <form id="confirmForm">
                                    <div class="field-group">
                                        <label class="form-label"><strong>Full Name</strong> <span class="text-danger">*</span></label>
                                        <input type="text" class="form-control" name="full_name" value="{{ data.get('full_name', '') }}" required>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <label class="form-label">First Name</label>
                                            <input type="text" class="form-control" name="first_name" value="{{ data.get('first_name', '') }}">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">Last Name</label>
                                            <input type="text" class="form-control" name="last_name" value="{{ data.get('last_name', '') }}">
                                        </div>
                                    </div>
                                    <div class="field-group">
                                        <label class="form-label"><strong>Email</strong> <span class="text-danger">*</span></label>
                                        <input type="email" class="form-control" name="email" value="{{ data.get('email', '') }}" required>
                                    </div>
                                    <div class="field-group">
                                        <label class="form-label">Mobile Number</label>
                                        <input type="text" class="form-control" name="handphone_number" value="{{ data.get('handphone_number', '') }}">
                                    </div>
                                    <div class="field-group">
                                        <label class="form-label">Job Title</label>
                                        <input type="text" class="form-control" name="job_title" value="{{ data.get('job_title', '') }}">
                                    </div>
                                    <div class="field-group">
                                        <label class="form-label">Company Name</label>
                                        <input type="text" class="form-control" name="company_name" value="{{ data.get('company_name', '') }}">
                                    </div>
                                    <div class="field-group">
                                        <label class="form-label">Company Website</label>
                                        <input type="url" class="form-control" name="company_website" value="{{ data.get('company_website', '') }}">
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <label class="form-label">City</label>
                                            <input type="text" class="form-control" name="city" value="{{ data.get('city', '') }}">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label"><strong>Country</strong> <span class="text-danger">*</span></label>
                                            <input type="text" class="form-control" name="country" value="{{ data.get('country', '') }}" required>
                                        </div>
                                    </div>
                                    <div class="text-center mt-4">
                                        <button type="submit" class="btn btn-success btn-custom me-2">
                                            <span id="saveText">Save to Google Sheet</span>
                                            <span id="saveSpinner" class="spinner-border spinner-border-sm ms-2" style="display: none;"></span>
                                        </button>
                                        <button type="button" class="btn btn-secondary btn-custom" onclick="location.reload()">Start Over</button>
                                    </div>
                                </form>
                            </div>
                        </div>

                        {% elif step == 'success' %}
                        <div class="text-center">
                            <div class="mb-4">
                                <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="text-success">Data Saved Successfully!</h4>
                            <p class="text-muted">Contact information has been sent to your Google Sheet.</p>
                            <div class="mt-4">
                                <button class="btn btn-primary btn-custom me-2" onclick="startNewSession()">Process Another Card</button>
                                <button class="btn btn-outline-secondary btn-custom" onclick="finishSession()">Finish Session</button>
                            </div>
                        </div>

                        {% elif step == 'error' %}
                        <div class="text-center">
                            <div class="mb-4">
                                <i class="bi bi-exclamation-triangle-fill text-warning" style="font-size: 4rem;"></i>
                            </div>
                            <h4 class="text-warning">Processing Error</h4>
                            <p class="text-muted">{{ error_message }}</p>
                            <div class="mt-4">
                                <button class="btn btn-primary btn-custom" onclick="location.reload()">Try Again</button>
                            </div>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function previewImage(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('uploadContent').style.display = 'none';
                    document.getElementById('imagePreview').style.display = 'block';
                    document.getElementById('previewImg').src = e.target.result;
                    document.getElementById('processBtn').disabled = false;
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        document.getElementById('uploadForm')?.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const imageInput = document.getElementById('imageInput');
            
            if (!imageInput.files[0]) {
                alert('Please select an image first');
                return;
            }
            
            formData.append('image', imageInput.files[0]);
            
            // Show loading state
            document.getElementById('btnText').textContent = 'Processing...';
            document.getElementById('btnSpinner').style.display = 'inline-block';
            document.getElementById('processBtn').disabled = true;
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    location.reload();
                } else {
                    throw new Error('Processing failed');
                }
            } catch (error) {
                alert('Error processing image. Please try again.');
                document.getElementById('btnText').textContent = 'Process Business Card';
                document.getElementById('btnSpinner').style.display = 'none';
                document.getElementById('processBtn').disabled = false;
            }
        });

        document.getElementById('confirmForm')?.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            // Show loading state
            document.getElementById('saveText').textContent = 'Saving...';
            document.getElementById('saveSpinner').style.display = 'inline-block';
            
            try {
                const response = await fetch('/save', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    location.reload();
                } else {
                    throw new Error('Save failed');
                }
            } catch (error) {
                alert('Error saving data. Please try again.');
                document.getElementById('saveText').textContent = 'Save to Google Sheet';
                document.getElementById('saveSpinner').style.display = 'none';
            }
        });

        function startNewSession() {
            fetch('/new-card', {method: 'POST'})
                .then(() => location.reload());
        }

        function finishSession() {
            fetch('/finish', {method: 'POST'})
                .then(() => {
                    alert('Session completed! Thank you for using Business Card Extractor.');
                    location.reload();
                });
        }
    </script>
</body>
</html>
"""

def extract_business_card_info(image_base64):
    """Extract business card information using GPT-4 Vision"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are a business card OCR expert specializing in Asian business cards. Extract the following information from the business card image and return it as a JSON object:

Required fields:
- full_name (always required)
- email (required)
- country (required - infer if not explicitly stated)

Optional fields:
- first_name (only if you can confidently split Western names)
- last_name (only if you can confidently split Western names)
- handphone_number
- job_title
- company_name
- company_website
- city

Name handling rules:
- If the name is clearly Western format (e.g., "John Smith"), split into first_name and last_name
- If unsure or Asian format, put the full name in full_name field only
- Always include full_name regardless of whether you split it

Return only valid JSON with no additional text."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please extract the business card information from this image:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON from the response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found in response")
                
    except Exception as e:
        print(f"Error in GPT-4 Vision processing: {str(e)}")
        return None

def send_to_webhook(data):
    """Send extracted data to Zapier webhook"""
    try:
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        response = requests.post(
            ZAPIER_WEBHOOK_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return False

@app.route('/')
def index():
    if 'step' not in session:
        session['step'] = 'upload'
    
    return render_template_string(HTML_TEMPLATE, 
                                step=session.get('step', 'upload'),
                                data=session.get('extracted_data', {}),
                                image_data=session.get('image_data', ''),
                                error_message=session.get('error_message', ''))

@app.route('/process', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            session['step'] = 'error'
            session['error_message'] = 'No image file provided'
            return jsonify({'error': 'No image file'}), 400
        
        file = request.files['image']
        if file.filename == '':
            session['step'] = 'error'
            session['error_message'] = 'No image file selected'
            return jsonify({'error': 'No file selected'}), 400
        
        # Read and encode image
        image_data = base64.b64encode(file.read()).decode('utf-8')
        session['image_data'] = image_data
        
        # Extract information using GPT-4 Vision
        extracted_data = extract_business_card_info(image_data)
        
        if extracted_data is None:
            session['step'] = 'error'
            session['error_message'] = 'Failed to extract information from the business card. Please ensure the image is clear and try again.'
            return jsonify({'error': 'Extraction failed'}), 500
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'country']
        missing_fields = [field for field in required_fields if not extracted_data.get(field)]
        
        if missing_fields:
            # Set empty values for missing required fields so user can fill them manually
            for field in missing_fields:
                extracted_data[field] = ''
        
        session['extracted_data'] = extracted_data
        session['step'] = 'confirm'
        
        return jsonify({'success': True})
        
    except Exception as e:
        session['step'] = 'error'
        session['error_message'] = f'An unexpected error occurred: {str(e)}'
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save_data():
    try:
        # Get form data
        form_data = {
            'timestamp': datetime.now().isoformat(),
            'full_name': request.form.get('full_name', ''),
            'first_name': request.form.get('first_name', ''),
            'last_name': request.form.get('last_name', ''),
            'email': request.form.get('email', ''),
            'handphone_number': request.form.get('handphone_number', ''),
            'job_title': request.form.get('job_title', ''),
            'company_name': request.form.get('company_name', ''),
            'company_website': request.form.get('company_website', ''),
            'city': request.form.get('city', ''),
            'country': request.form.get('country', '')
        }
        
        # Validate required fields
        if not form_data['full_name'] or not form_data['email'] or not form_data['country']:
            session['step'] = 'error'
            session['error_message'] = 'Please fill in all required fields (Full Name, Email, Country)'
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Send to webhook
        if send_to_webhook(form_data):
            session['step'] = 'success'
            # Store in session for potential batch processing
            if 'session_cards' not in session:
                session['session_cards'] = []
            session['session_cards'].append(form_data)
        else:
            session['step'] = 'error'
            session['error_message'] = 'Failed to save data to Google Sheet. Please check your connection and try again.'
            return jsonify({'error': 'Webhook failed'}), 500
        
        return jsonify({'success': True})
        
    except Exception as e:
        session['step'] = 'error'
        session['error_message'] = f'Error saving data: {str(e)}'
        return jsonify({'error': str(e)}), 500

@app.route('/new-card', methods=['POST'])
def new_card():
    # Reset for new card but keep session data
    session['step'] = 'upload'
    session.pop('extracted_data', None)
    session.pop('image_data', None)
    session.pop('error_message', None)
    return jsonify({'success': True})

@app.route('/finish', methods=['POST'])
def finish_session():
    # Clear all session data
    session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)