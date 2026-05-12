# Multimedia Steganography Web Application

A full-stack web application for hiding and extracting secret data in various media files using steganography techniques.

## Features
 - Text Steganography
 Image Steganography
 - Audio Steganography  
 - Video Steganography
 - Voice Steganography
 - AES encryption for secret data
 -Secure data extraction
 - User-friendly interface


## Project Structure
```
multimedia-steganography/
│
├── backend/
│   ├── steganography/
│   │   ├── __init__.py
│   │   ├── audio_stego.py
│   │   ├── crypto.py
│   │   ├── image_stego.py
│   │   ├── text_stego.py
│   │   ├── video_stego.py
│   │   └── voice_stego.py
│   │
│   ├── uploads/
│   ├── app.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│
├── uploads/
│
├── IMPLEMENTATION_DOCUMENTATION.md
├── PROJECT_IMPLEMENTATION_DOCUMENTATION.md
├── README.md
├── TODO.md
│
├── start_all.bat
├── start_backend.bat
└── start_frontend.bat
```
## Modules Included

- Image Steganography
- Audio Steganography
- Video Steganography
- Voice Steganography
- Text Encryption & Security


## Setup Instructions

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```
## Tech Stack

- **Frontend**: React, Tailwind CSS
- **Backend**: Flask (Python)
- **Libraries**:
  - Pillow
  - pycryptodome
  - OpenCV
  - NumPy
  - Flask-CORS
  - 
## Future Improvements

- Video extraction functionality is currently under development and will be optimized in future updates.

