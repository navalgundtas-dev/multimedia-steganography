# Steganography Web Application

A full-stack web application for hiding and extracting secret data in various media files using steganography techniques.

## Features

- 🖼️ Image Steganography
- 🎵 Audio Steganography  
- 🎬 Video Steganography
- 🎙️ Voice Steganography
- AES encryption for secret data
- User-friendly React interface
- Flask backend API

## Project Structure

```
stegnography/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── steganography/
│   │   ├── __init__.py
│   │   ├── image_stego.py     # Image steganography logic
│   │   ├── audio_stego.py     # Audio steganography logic
│   │   ├── video_stego.py     # Video steganography logic
│   │   ├── voice_stego.py     # Voice steganography logic
│   │   └── crypto.py          # AES encryption/decryption
│   └── uploads/               # Temporary file storage
├── frontend/
│   ├── package.json
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageStego.jsx
│   │   │   ├── AudioStego.jsx
│   │   │   ├── VideoStego.jsx
│   │   │   ├── VoiceStego.jsx
│   │   │   ├── About.jsx
│   │   │   └── Navbar.jsx
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   └── tailwind.config.js
└── README.md
```

## Setup Instructions

### Backend Setup
1. Navigate to backend directory
2. Install dependencies: `pip install -r requirements.txt`
3. Run Flask app: `python app.py`

### Frontend Setup
1. Navigate to frontend directory
2. Install dependencies: `npm install`
3. Start development server: `npm start`

## Tech Stack

- **Frontend**: React, Tailwind CSS
- **Backend**: Flask (Python)
- **Libraries**: Pillow, pydub, moviepy, pycryptodome



