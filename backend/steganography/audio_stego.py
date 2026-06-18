"""
Audio steganography implementation using LSB (Least Significant Bit) technique for WAV files
"""
import os
import struct
import wave
from typing import Tuple, Optional
from .crypto import encrypt_data, decrypt_data


class AudioSteganography:
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        self.supported_formats = ('.wav',)
    
    def _int_to_bin(self, value: int, bits: int = 8) -> str:
        """Convert integer to binary string"""
        return format(value, f'0{bits}b')
    
    def _bin_to_int(self, binary: str) -> int:
        """Convert binary string to integer"""
        return int(binary, 2)
    
    def _get_audio_capacity(self, audio_file: wave.Wave_read) -> int:
        """Calculate maximum data capacity of audio file"""
        frames = audio_file.getnframes()
        sample_width = audio_file.getsampwidth()
        channels = audio_file.getnchannels()
        
        # Each sample can hide 1 bit, so total bits = frames * channels
        # Divide by 8 to get bytes
        return (frames * channels) // 8
    
    def embed_data(self, cover_audio_path: str, secret_data: bytes, password: str, output_path: str) -> bool:
        """
        Embed secret data into cover audio using LSB technique
        
        Args:
            cover_audio_path: Path to cover audio file
            secret_data: Secret data to hide
            password: Password for encryption
            output_path: Path for output stego audio
            
        Returns:
            bool: Success status
        """
        try:
            # Open audio file
            with wave.open(cover_audio_path, 'rb') as audio_in:
                # Get audio parameters
                params = audio_in.getparams()
                frames = audio_in.getnframes()
                
                # Check capacity
                capacity = self._get_audio_capacity(audio_in)
                if len(secret_data) > capacity:
                    raise ValueError(f"Secret data too large. Max capacity: {capacity} bytes")
                
                # Read all audio frames
                audio_in.rewind()
                audio_frames = audio_in.readframes(frames)
                
                # Encrypt secret data
                encrypted_data = encrypt_data(secret_data, password)
                
                # Add length header (4 bytes) + encrypted data
                data_to_hide = struct.pack('>I', len(encrypted_data)) + encrypted_data
                
                # Convert to binary
                binary_data = ''.join(self._int_to_bin(byte) for byte in data_to_hide)
                
                # Add end marker (32 bits of 1s to mark end of data)
                binary_data += '1' * 32
                
                # Convert audio frames to bytearray for modification
                audio_bytes = bytearray(audio_frames)
                
                # Embed data bit by bit in LSB of audio samples
                bit_index = 0
                sample_width = params.sampwidth
                channels = params.nchannels
                
                for i in range(0, len(audio_bytes), sample_width * channels):
                    if bit_index >= len(binary_data):
                        break
                    
                    # Process each channel in the sample
                    for channel in range(channels):
                        if bit_index >= len(binary_data):
                            break
                        
                        sample_idx = i + (channel * sample_width)
                        if sample_idx + sample_width > len(audio_bytes):
                            break
                        
                        # Get sample value (handle different sample widths)
                        if sample_width == 1:
                            sample = audio_bytes[sample_idx]
                            # Modify LSB
                            sample = (sample & 0xFE) | int(binary_data[bit_index])
                            audio_bytes[sample_idx] = sample
                        elif sample_width == 2:
                            # 16-bit sample (little-endian)
                            sample = struct.unpack('<H', bytes(audio_bytes[sample_idx:sample_idx+2]))[0]
                            # Modify LSB
                            sample = (sample & 0xFFFE) | int(binary_data[bit_index])
                            audio_bytes[sample_idx:sample_idx+2] = struct.pack('<H', sample)
                        elif sample_width == 3:
                            # 24-bit sample (little-endian)
                            sample_bytes = audio_bytes[sample_idx:sample_idx+3] + b'\x00'
                            sample = struct.unpack('<I', sample_bytes)[0]
                            # Modify LSB
                            sample = (sample & 0xFFFFFFFE) | int(binary_data[bit_index])
                            new_bytes = struct.pack('<I', sample)[:3]
                            audio_bytes[sample_idx:sample_idx+3] = new_bytes
                        elif sample_width == 4:
                            # 32-bit sample (little-endian)
                            sample = struct.unpack('<I', bytes(audio_bytes[sample_idx:sample_idx+4]))[0]
                            # Modify LSB
                            sample = (sample & 0xFFFFFFFE) | int(binary_data[bit_index])
                            audio_bytes[sample_idx:sample_idx+4] = struct.pack('<I', sample)
                        
                        bit_index += 1
                
                # Write modified audio to output file
                with wave.open(output_path, 'wb') as audio_out:
                    audio_out.setparams(params)
                    audio_out.writeframes(bytes(audio_bytes))
            
            return True
            
        except Exception as e:
            print(f"Embedding failed: {str(e)}")
            return False
    
    def extract_data(self, stego_audio_path: str, password: str) -> Optional[bytes]:
        """
        Extract secret data from stego audio

        Args:
            stego_audio_path: Path to stego audio file
            password: Password for decryption

        Returns:
            bytes: Extracted secret data or None if failed
        """
        try:
            with wave.open(stego_audio_path, 'rb') as audio:
                # Get audio parameters
                params = audio.getparams()
                frames = audio.getnframes()

                # Read all audio frames
                audio.rewind()
                audio_frames = audio.readframes(frames)
                audio_bytes = bytearray(audio_frames)

                binary_data = ""
                sample_width = params.sampwidth
                channels = params.nchannels

                # Extract binary data from LSBs until we find the end marker
                end_marker = '1' * 32
                found_end_marker = False

                for i in range(0, len(audio_bytes), sample_width * channels):
                    if found_end_marker:
                        break

                    # Process each channel in the sample
                    for channel in range(channels):
                        sample_idx = i + (channel * sample_width)
                        if sample_idx + sample_width > len(audio_bytes):
                            break

                        # Get LSB from sample
                        if sample_width == 1:
                            sample = audio_bytes[sample_idx]
                            lsb = str(sample & 1)
                        elif sample_width == 2:
                            sample = struct.unpack('<H', bytes(audio_bytes[sample_idx:sample_idx+2]))[0]
                            lsb = str(sample & 1)
                        elif sample_width == 3:
                            sample_bytes = audio_bytes[sample_idx:sample_idx+3] + b'\x00'
                            sample = struct.unpack('<I', sample_bytes)[0]
                            lsb = str(sample & 1)
                        elif sample_width == 4:
                            sample = struct.unpack('<I', bytes(audio_bytes[sample_idx:sample_idx+4]))[0]
                            lsb = str(sample & 1)
                        else:
                            continue

                        binary_data += lsb

                        # Check for end marker
                        if len(binary_data) >= 32 and binary_data[-32:] == end_marker:
                            found_end_marker = True
                            # Remove end marker
                            binary_data = binary_data[:-32]
                            break

                if not found_end_marker:
                    raise ValueError("No valid steganography data found in audio")

                # Ensure binary string length is multiple of 8
                if len(binary_data) % 8 != 0:
                    raise ValueError("Extracted data length is not valid (not multiple of 8 bits)")

                # Convert binary to bytes
                extracted_bytes = bytearray()
                for i in range(0, len(binary_data), 8):
                    byte_binary = binary_data[i:i+8]
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
    
    def validate_audio(self, audio_path: str) -> Tuple[bool, str]:
        """
        Validate if audio file is suitable for steganography
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(audio_path):
                return False, "Audio file not found"
            
            if not audio_path.lower().endswith(self.supported_formats):
                return False, f"Unsupported format. Supported: {', '.join(self.supported_formats)}"
            
            file_size = os.path.getsize(audio_path)
            if file_size > self.max_file_size:
                return False, f"File too large. Max size: {self.max_file_size // (1024*1024)}MB"
            
            # Try to open as WAV file
            with wave.open(audio_path, 'rb') as audio:
                frames = audio.getnframes()
                if frames < 1000:  # Minimum 1000 frames
                    return False, "Audio file too short. Minimum 1000 frames required"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid audio file: {str(e)}"















