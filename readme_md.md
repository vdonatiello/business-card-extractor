# Business Card Extractor

A web application that extracts contact information from business card images using GPT-4 Vision and automatically saves the data to Google Sheets via Zapier webhook.

## Features

- 📱 Mobile-optimized interface (iPhone Safari ready)
- 🔍 GPT-4 Vision OCR for intelligent text extraction
- 🌏 Smart name handling for Asian and Western formats
- 📊 Direct Google Sheets integration via Zapier
- 🔄 Session management for multiple cards
- ✅ Manual confirmation and editing of extracted data

## Setup Instructions

### 1. Environment Variables

Set these in your Vercel dashboard (Project → Settings → Environment Variables):

```
OPENAI_API_KEY=your-openai-api-key-here
ZAPIER_WEBHOOK_URL=your-zapier-webhook-url-here
```

### 2. Required Fields

The app extracts and requires:
- **Full Name** (required)
- **Email** (required) 
- **Country** (required)

Optional fields:
- First Name, Last Name (if confidently split)
- Mobile Number, Job Title, Company Name, Company Website, City

### 3. Usage

1. Upload business card image from iPhone camera
2. Review and edit extracted information
3. Save directly to Google Sheets
4. Process multiple cards in one session

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: OpenAI GPT-4 Vision API
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Deployment**: Vercel
- **Integration**: Zapier webhook → Google Sheets

## Development

```bash
pip install -r requirements.txt
python app.py
```

The app will run on `http://localhost:5000`

## Important Notes

- Optimized for Asian business networking
- Handles both portrait and landscape card orientations
- Best results with good lighting and clear text
- Supports JPG and PNG image formats