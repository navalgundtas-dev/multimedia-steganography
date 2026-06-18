"""
Video steganography implementation using LSB technique on MP4 frames
"""
import os
import struct
import cv2
import numpy as np
from typing import Tuple, Optional
from .crypto import encrypt_data, decrypt_data


class VideoSteganography:
    def __init__(self):
        self.max_file_size = 100 * 1024 * 1024  # 100MB limit
        self.supported_formats = ('.mp4', '.avi', '.mov')
    
    def _int_to_bin(self, value: int, bits: int = 8) -> str:
        """Convert integer to binary string"""
        return format(value, f'0{bits}b')
    
    def _bin_to_int(self, binary: str) -> int:
        """Convert binary string to integer"""
        return int(binary, 2)
    
    def _get_video_capacity(self, video_path: str) -> int:
        """Calculate maximum data capacity of video file"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return 0
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        # Each pixel can hide 3 bits (RGB channels), so total bytes = frames * width * height * 3 / 8
        # Use only first frame for capacity estimation (simple approach)
        return (width * height * 3) // 8
    
    def embed_data(self, cover_video_path: str, secret_data: bytes, password: str, output_path: str) -> bool:
        """
        Embed secret data into cover video using LSB technique on frames
        
        Args:
            cover_video_path: Path to cover video file
            secret_data: Secret data to hide
            password: Password for encryption
            output_path: Path for output stego video
            
        Returns:
            bool: Success status
        """
        try:
            # Open video
            cap = cv2.VideoCapture(cover_video_path)
            if not cap.isOpened():
                raise ValueError("Cannot open video file")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Check capacity (using first frame as estimate)
            capacity = (width * height * 3) // 8
            if len(secret_data) > capacity:
                cap.release()
                raise ValueError(f"Secret data too large. Max capacity: {capacity} bytes per frame")
            
            # Encrypt secret data
            encrypted_data = encrypt_data(secret_data, password)
            
            # Add length header (4 bytes) + encrypted data
            data_to_hide = struct.pack('>I', len(encrypted_data)) + encrypted_data
            
            # Convert to binary
            binary_data = ''.join(self._int_to_bin(byte) for byte in data_to_hide)
            
            # Add end marker (32 bits of 1s)
            binary_data += '1' * 32
            
            # Prepare video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            bit_index = 0
            data_embedded = False
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Embed data in first frame only (simple approach)
                if frame_count == 0 and not data_embedded:
                    # Convert frame to RGB if needed
                    if len(frame.shape) == 3:
                        if frame.shape[2] == 4:  # BGRA
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        elif frame.shape[2] == 1:  # Grayscale
                            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                    
                    # Embed data in frame
                    pixels = frame.flatten()
                    
                    for i in range(len(pixels)):
                        if bit_index >= len(binary_data):
                            data_embedded = True
                            break
                        
                        # Modify LSB of pixel
                        pixels[i] = (pixels[i] & 0xFE) | int(binary_data[bit_index])
                        bit_index += 1
                    
                    # Reshape back to frame
                    frame = pixels.reshape(frame.shape).astype(frame.dtype)
                    data_embedded = True
                
                # Write frame
                out.write(frame)
                frame_count += 1
            
            cap.release()
            out.release()
            
            return True
            
        except Exception as e:
            print(f"Embedding failed: {str(e)}")
            return False
    
    def extract_data(self, stego_video_path: str, password: str) -> Optional[bytes]:
        """
        Extract secret data from stego video
        
        Args:
            stego_video_path: Path to stego video file
            password: Password for decryption
            
        Returns:
            bytes: Extracted secret data or None if failed
        """
        try:
            cap = cv2.VideoCapture(stego_video_path)
            if not cap.isOpened():
                raise ValueError("Cannot open video file")
            
            # Read first frame
            ret, frame = cap.read()
            if not ret:
                cap.release()
                raise ValueError("Cannot read video frame")
            
            # Convert frame to RGB if needed
            if len(frame.shape) == 3:
                if frame.shape[2] == 4:  # BGRA
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                elif frame.shape[2] == 1:  # Grayscale
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
            cap.release()
            
            # Extract binary data from LSBs
            pixels = frame.flatten()
            binary_data = ""
            end_marker = '1' * 32
            found_end_marker = False
            
            for pixel in pixels:
                if found_end_marker:
                    break
                
                # Get LSB
                lsb = str(pixel & 1)
                binary_data += lsb
                
                # Check for end marker
                if len(binary_data) >= 32 and binary_data[-32:] == end_marker:
                    found_end_marker = True
                    # Remove end marker
                    binary_data = binary_data[:-32]
                    break
            
            if not found_end_marker:
                raise ValueError("No valid steganography data found in video")
            
            # Convert binary to bytes
            extracted_bytes = bytearray()
            for i in range(0, len(binary_data), 8):
                byte_binary = binary_data[i:i+8]
                if len(byte_binary) == 8:
                    extracted_bytes.append(self._bin_to_int(byte_binary))
            
            # Extract length header
            if len(extracted_bytes) < 4:
                raise ValueError("Invalid stego data: insufficient bytes")
            
            data_length = struct.unpack('>I', bytes(extracted_bytes[:4]))[0]
            
            # Validate data length
            if data_length <= 0 or data_length > len(extracted_bytes) - 4:
                raise ValueError("Invalid stego data: corrupted length header")
            
            encrypted_data = bytes(extracted_bytes[4:4+data_length])
            
            # Decrypt data
            decrypted_data = decrypt_data(encrypted_data, password)
            
            return decrypted_data
                
        except Exception as e:
            print(f"Extraction failed: {str(e)}")
            return None
    
    def validate_video(self, video_path: str) -> Tuple[bool, str]:
        """
        Validate if video file is suitable for steganography
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(video_path):
                return False, "Video file not found"
            
            if not video_path.lower().endswith(self.supported_formats):
                return False, f"Unsupported format. Supported: {', '.join(self.supported_formats)}"
            
            file_size = os.path.getsize(video_path)
            if file_size > self.max_file_size:
                return False, f"File too large. Max size: {self.max_file_size // (1024*1024)}MB"
            
            # Try to open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, "Cannot open video file"
            
            # Check if we can read at least one frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return False, "Cannot read video frames"
            
            if frame.size < 1000:  # Minimum 1000 pixels
                return False, "Video frame too small. Minimum 1000 pixels required"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid video file: {str(e)}"
