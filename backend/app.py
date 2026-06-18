"""
Flask backend for Steganography Web Application
"""

import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from steganography.image_stego import ImageSteganography
from steganography.audio_stego import AudioSteganography
from steganography.video_stego import VideoSteganography
from steganography.text_stego import TextSteganography
from steganography.voice_stego import VoiceSteganography

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'mp3', 'wav', 'mp4', 'avi', 'mov'}

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize steganography modules
image_stego = ImageSteganography()
audio_stego = AudioSteganography()
video_stego = VideoSteganography()
text_stego = TextSteganography()
voice_stego = VoiceSteganography()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    """Generate unique filename for temporary storage"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Steganography API is running'})


# Image Steganography Routes
@app.route('/api/image/embed', methods=['POST'])
def embed_image():
    """Embed secret data into image"""
    try:
        # Check if files are present
        if 'cover_image' not in request.files:
            return jsonify({'error': 'No cover image provided'}), 400
        
        cover_file = request.files['cover_image']
        if cover_file.filename == '':
            return jsonify({'error': 'No cover image selected'}), 400
        
        if not allowed_file(cover_file.filename):
            return jsonify({'error': 'Invalid file type for cover image'}), 400
        
        # Get secret data
        secret_text = request.form.get('secret_text', '').strip()
        secret_file = request.files.get('secret_file')
        password = request.form.get('password', '').strip()
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not secret_text and not secret_file:
            return jsonify({'error': 'Either secret text or secret file is required'}), 400
        
        # Prepare secret data
        if secret_file and secret_file.filename:
            secret_data = secret_file.read()
        else:
            secret_data = secret_text.encode('utf-8')
        
        # Validate cover image
        cover_filename = generate_unique_filename(cover_file.filename)
        cover_path = os.path.join(UPLOAD_FOLDER, cover_filename)
        cover_file.save(cover_path)
        
        is_valid, error_msg = image_stego.validate_image(cover_path)
        if not is_valid:
            os.remove(cover_path)
            return jsonify({'error': error_msg}), 400
        
        # Generate output filename
        output_filename = f"stego_{cover_filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Embed data
        success = image_stego.embed_data(cover_path, secret_data, password, output_path)
        
        # Clean up cover image
        os.remove(cover_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Data embedded successfully',
                'download_url': f'/api/download/{output_filename}'
            })
        else:
            if os.path.exists(output_path):
                os.remove(output_path)
            return jsonify({'error': 'Failed to embed data'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/image/extract', methods=['POST'])
def extract_image():
    """Extract secret data from stego image"""
    try:
        if 'stego_image' not in request.files:
            return jsonify({'error': 'No stego image provided'}), 400
        
        stego_file = request.files['stego_image']
        if stego_file.filename == '':
            return jsonify({'error': 'No stego image selected'}), 400
        
        password = request.form.get('password', '').strip()
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Save uploaded file
        stego_filename = generate_unique_filename(stego_file.filename)
        stego_path = os.path.join(UPLOAD_FOLDER, stego_filename)
        stego_file.save(stego_path)
        
        # Validate image first
        is_valid, error_msg = image_stego.validate_image(stego_path)
        if not is_valid:
            os.remove(stego_path)
            return jsonify({'error': f'Invalid image: {error_msg}'}), 400
        
        # Extract data
        try:
            extracted_data = image_stego.extract_data(stego_path, password)
        except ValueError as e:
            os.remove(stego_path)
            return jsonify({'error': str(e)}), 400
        
        # Clean up
        os.remove(stego_path)
        
        if extracted_data is not None:
            # Try to decode as text first
            try:
                text_data = extracted_data.decode('utf-8')
                return jsonify({
                    'success': True,
                    'message': 'Data extracted successfully',
                    'data_type': 'text',
                    'data': text_data
                })
            except UnicodeDecodeError:
                # Return as file download
                output_filename = f"extracted_{stego_filename}.bin"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(extracted_data)
                
                return jsonify({
                    'success': True,
                    'message': 'Data extracted successfully',
                    'data_type': 'file',
                    'download_url': f'/api/download/{output_filename}'
                })
        else:
            return jsonify({
                'error': 'Failed to extract data. Possible reasons:\n'
                        '• Wrong password\n'
                        '• Image does not contain steganography data\n'
                        '• Image may be corrupted\n'
                        '• Image was not created with this application'
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated files"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/api/image/validate', methods=['POST'])
def validate_image():
    """Validate image file for steganography"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Save temporarily
        filename = generate_unique_filename(image_file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(file_path)
        
        # Validate
        is_valid, error_msg = image_stego.validate_image(file_path)
        
        # Clean up
        os.remove(file_path)
        
        if is_valid:
            return jsonify({'valid': True, 'message': 'Image is valid for steganography'})
        else:
            return jsonify({'valid': False, 'error': error_msg})
            
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500


# Audio Steganography Routes
@app.route('/encode/audio', methods=['POST'])
@app.route('/api/audio/embed', methods=['POST'])
def embed_audio():
    """Embed secret data into audio file"""
    try:
        if 'cover_audio' not in request.files:
            return jsonify({'error': 'No cover audio provided'}), 400
        
        cover_file = request.files['cover_audio']
        if cover_file.filename == '':
            return jsonify({'error': 'No cover audio selected'}), 400
        
        if not allowed_file(cover_file.filename):
            return jsonify({'error': 'Invalid file type for cover audio'}), 400
        
        # Get secret data
        secret_text = request.form.get('secret_text', '').strip()
        secret_file = request.files.get('secret_file')
        password = request.form.get('password', '').strip()
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not secret_text and not secret_file:
            return jsonify({'error': 'Either secret text or secret file is required'}), 400
        
        # Prepare secret data
        if secret_file and secret_file.filename:
            secret_data = secret_file.read()
        else:
            secret_data = secret_text.encode('utf-8')
        
        # Validate cover audio
        cover_filename = generate_unique_filename(cover_file.filename)
        cover_path = os.path.join(UPLOAD_FOLDER, cover_filename)
        cover_file.save(cover_path)
        
        is_valid, error_msg = audio_stego.validate_audio(cover_path)
        if not is_valid:
            os.remove(cover_path)
            return jsonify({'error': error_msg}), 400
        
        # Generate output filename
        output_filename = f"stego_audio_{cover_filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Embed data
        success = audio_stego.embed_data(cover_path, secret_data, password, output_path)
        
        # Clean up cover audio
        os.remove(cover_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Data embedded successfully',
                'download_url': f'/api/download/{output_filename}'
            })
        else:
            if os.path.exists(output_path):
                os.remove(output_path)
            return jsonify({'error': 'Failed to embed data'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/decode/audio', methods=['POST'])
@app.route('/api/audio/extract', methods=['POST'])
def extract_audio():
    """Extract secret data from stego audio"""
    try:
        if 'stego_audio' not in request.files:
            return jsonify({'error': 'No stego audio provided'}), 400
        
        stego_file = request.files['stego_audio']
        if stego_file.filename == '':
            return jsonify({'error': 'No stego audio selected'}), 400
        
        password = request.form.get('password', '').strip()
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Save uploaded file
        stego_filename = generate_unique_filename(stego_file.filename)
        stego_path = os.path.join(UPLOAD_FOLDER, stego_filename)
        stego_file.save(stego_path)
        
        # Validate audio first
        is_valid, error_msg = audio_stego.validate_audio(stego_path)
        if not is_valid:
            os.remove(stego_path)
            return jsonify({'error': f'Invalid audio: {error_msg}'}), 400
        
        # Extract data
        try:
            extracted_data = audio_stego.extract_data(stego_path, password)
        except ValueError as e:
            os.remove(stego_path)
            return jsonify({'error': str(e)}), 400
        
        # Clean up
        os.remove(stego_path)
        
        if extracted_data is not None:
            # Try to decode as text first
            try:
                text_data = extracted_data.decode('utf-8')
                return jsonify({
                    'success': True,
                    'message': 'Data extracted successfully',
                    'data_type': 'text',
                    'data': text_data
                })
            except UnicodeDecodeError:
                # Return as file download
                output_filename = f"extracted_audio_{stego_filename}.bin"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(extracted_data)
                
                return jsonify({
                    'success': True,
                    'message': 'Data extracted successfully',
                    'data_type': 'file',
                    'download_url': f'/api/download/{output_filename}'
                })
        else:
            return jsonify({
                'error': 'Failed to extract data. Possible reasons:\n'
                        '• Wrong password\n'
                        '• Audio does not contain steganography data\n'
                        '• Audio may be corrupted\n'
                        '• Audio was not created with this application'
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# Voice Steganography Routes
@app.route('/encode/voice', methods=['POST'])
@app.route('/api/voice/embed', methods=['POST'])
def embed_voice():
    """Embed secret data into voice recording using voiced frames."""
    try:
        voice_file = request.files.get('voice_file') or request.files.get('cover_voice')
        if not voice_file:
            return jsonify({'error': 'No voice recording provided'}), 400
        
        if voice_file.filename == '':
            return jsonify({'error': 'No voice recording selected'}), 400
        
        secret_text = request.form.get('secret_text', '').strip()
        secret_file = request.files.get('secret_file')
        password = request.form.get('password', '').strip()
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not secret_text and not (secret_file and secret_file.filename):
            return jsonify({'error': 'Either secret text or secret file is required'}), 400
        
        if secret_file and secret_file.filename:
            secret_data = secret_file.read()
        else:
            secret_data = secret_text.encode('utf-8')
        
        voice_filename = generate_unique_filename(voice_file.filename)
        voice_path = os.path.join(UPLOAD_FOLDER, voice_filename)
        voice_file.save(voice_path)
        
        is_valid, error_msg = voice_stego.validate_voice(voice_path)
        if not is_valid:
            os.remove(voice_path)
            return jsonify({'error': error_msg}), 400
        
        output_filename = f"stego_voice_{voice_filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        success = voice_stego.embed_data(voice_path, secret_data, password, output_path)
        
        os.remove(voice_path)
        
        if success:
            response = {
                'success': True,
                'message': 'Voice payload embedded successfully',
                'download_url': f'/api/download/{output_filename}',
            }
            report = voice_stego.get_last_report()
            if report:
                response['analysis'] = report
            return jsonify(response)
        else:
            if os.path.exists(output_path):
                os.remove(output_path)
            return jsonify({'error': 'Failed to embed data into voice recording'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/decode/voice', methods=['POST'])
@app.route('/api/voice/extract', methods=['POST'])
def extract_voice():
    """Extract hidden payload from a stego voice recording."""
    try:
        stego_file = request.files.get('stego_voice') or request.files.get('voice_file')
        if not stego_file:
            return jsonify({'error': 'No stego voice provided'}), 400
        
        if stego_file.filename == '':
            return jsonify({'error': 'No stego voice selected'}), 400
        
        password = request.form.get('password', '').strip()
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        stego_filename = generate_unique_filename(stego_file.filename)
        stego_path = os.path.join(UPLOAD_FOLDER, stego_filename)
        stego_file.save(stego_path)
        
        is_valid, error_msg = voice_stego.validate_voice(stego_path)
        if not is_valid:
            os.remove(stego_path)
            return jsonify({'error': f'Invalid voice recording: {error_msg}'}), 400
        
        try:
            extracted_data = voice_stego.extract_data(stego_path, password)
        except ValueError as e:
            os.remove(stego_path)
            return jsonify({'error': str(e)}), 400
        
        os.remove(stego_path)
        
        if extracted_data is None:
            return jsonify({
                'error': 'Failed to extract voice payload. Possible reasons:\n'
                         '• Wrong password\n'
                         '• Recording does not contain payload\n'
                         '• Recording may be corrupted or incompatible'
            }), 400
        
        report = voice_stego.get_last_report()
        
        try:
            text_data = extracted_data.decode('utf-8')
            response = {
                'success': True,
                'message': 'Voice payload extracted successfully',
                'data_type': 'text',
                'data': text_data,
            }
        except UnicodeDecodeError:
            output_filename = f"extracted_voice_{stego_filename}.bin"
            output_path = os.path.join(UPLOAD_FOLDER, output_filename)
            with open(output_path, 'wb') as f:
                f.write(extracted_data)
            response = {
                'success': True,
                'message': 'Voice payload extracted successfully',
                'data_type': 'file',
                'download_url': f'/api/download/{output_filename}',
            }
        
        if report:
            response['analysis'] = report
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Video Steganography Routes
@app.route('/encode/video', methods=['POST'])
@app.route('/api/video/embed', methods=['POST'])
def embed_video():
    """Embed secret data into video file"""
    try:
        if 'cover_video' not in request.files:
            return jsonify({'error': 'No cover video provided'}), 400
        
        cover_file = request.files['cover_video']
        if cover_file.filename == '':
            return jsonify({'error': 'No cover video selected'}), 400
        
        if not allowed_file(cover_file.filename):
            return jsonify({'error': 'Invalid file type for cover video'}), 400
        
        # Get secret data
        secret_text = request.form.get('secret_text', '').strip()
        secret_file = request.files.get('secret_file')
        password = request.form.get('password', '').strip()
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not secret_text and not secret_file:
            return jsonify({'error': 'Either secret text or secret file is required'}), 400
        
        # Prepare secret data
        if secret_file and secret_file.filename:
            secret_data = secret_file.read()
        else:
            secret_data = secret_text.encode('utf-8')
        
        # Validate cover video
        cover_filename = generate_unique_filename(cover_file.filename)
        cover_path = os.path.join(UPLOAD_FOLDER, cover_filename)
        cover_file.save(cover_path)
        
        is_valid, error_msg = video_stego.validate_video(cover_path)
        if not is_valid:
            os.remove(cover_path)
            return jsonify({'error': error_msg}), 400
        
        # Generate output filename
        output_filename = f"stego_video_{cover_filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Embed data
        success = video_stego.embed_data(cover_path, secret_data, password, output_path)
        
        # Clean up cover video
        os.remove(cover_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Data embedded successfully',
                'download_url': f'/api/download/{output_filename}'
            })
        else:
            if os.path.exists(output_path):
                os.remove(output_path)
            return jsonify({'error': 'Failed to embed data'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/decode/video', methods=['POST'])
@app.route('/api/video/extract', methods=['POST'])
def extract_video():
    """Extract secret data from stego video"""
    try:
        if 'stego_video' not in request.files:
            return jsonify({'error': 'No stego video provided'}), 400
        
        stego_file = request.files['stego_video']
        if stego_file.filename == '':
            return jsonify({'error': 'No stego video selected'}), 400
        
        password = request.form.get('password', '').strip()
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Save uploaded file
        stego_filename = generate_unique_filename(stego_file.filename)
        stego_path = os.path.join(UPLOAD_FOLDER, stego_filename)
        stego_file.save(stego_path)
        
        # Validate video first
        is_valid, error_msg = video_stego.validate_video(stego_path)
        if not is_valid:
            os.remove(stego_path)
            return jsonify({'error': f'Invalid video: {error_msg}'}), 400
        
        # Extract data
        try:
            extracted_data = video_stego.extract_data(stego_path, password)
        except ValueError as e:
            os.remove(stego_path)
            return jsonify({'error': str(e)}), 400
        
        # Clean up
        os.remove(stego_path)
        
        if extracted_data is not None:
            # Try to decode as text first
            try:
                text_data = extracted_data.decode('utf-8')
                return jsonify({
                    'success': True,
                    'message': 'Data extracted successfully',
                    'data_type': 'text',
                    'data': text_data
                })
            except UnicodeDecodeError:
                # Return as file download
                output_filename = f"extracted_video_{stego_filename}.bin"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(extracted_data)
                
                return jsonify({
                    'success': True,
                    'message': 'Data extracted successfully',
                    'data_type': 'file',
                    'download_url': f'/api/download/{output_filename}'
                })
        else:
            return jsonify({
                'error': 'Failed to extract data. Possible reasons:\n'
                        '• Wrong password\n'
                        '• Video does not contain steganography data\n'
                        '• Video may be corrupted\n'
                        '• Video was not created with this application'
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500





# Text Steganography Routes
@app.route('/encode/text', methods=['POST'])
@app.route('/api/text/encode', methods=['POST'])
def encode_text():
    """Encode secret text into cover text"""
    try:
        data = request.get_json()
        
        cover_text = data.get('cover_text', '').strip()
        secret_text = data.get('secret_text', '').strip()
        password = data.get('password', '').strip()
        
        if not cover_text:
            return jsonify({'error': 'Cover text is required'}), 400
        
        if not secret_text:
            return jsonify({'error': 'Secret text is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate cover text
        is_valid, error_msg = text_stego.validate_text(cover_text)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Encode data
        try:
            stego_text = text_stego.encode(cover_text, secret_text, password)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        return jsonify({
            'success': True,
            'message': 'Text encoded successfully',
            'stego_text': stego_text
        })
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/decode/text', methods=['POST'])
@app.route('/api/text/decode', methods=['POST'])
def decode_text():
    """Decode secret text from stego text"""
    try:
        data = request.get_json()
        
        stego_text = data.get('stego_text', '').strip()
        password = data.get('password', '').strip()
        
        if not stego_text:
            return jsonify({'error': 'Stego text is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Decode data
        try:
            secret_text = text_stego.decode(stego_text, password)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        if secret_text is not None:
            return jsonify({
                'success': True,
                'message': 'Text decoded successfully',
                'secret_text': secret_text
            })
        else:
            return jsonify({
                'error': 'Failed to decode text. Possible reasons:\n'
                        '• Wrong password\n'
                        '• Text does not contain steganography data\n'
                        '• Text may be corrupted\n'
                        '• Text was not created with this application'
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
