"""
Text steganography implementation using zero-width Unicode characters
"""
from typing import Tuple, Optional
from .crypto import encrypt_data, decrypt_data


class TextSteganography:
    def __init__(self):
        # Zero-width characters used for encoding
        self.ZERO_WIDTH_SPACE = '\u200B'  # Zero Width Space
        self.ZERO_WIDTH_NON_JOINER = '\u200C'  # Zero Width Non-Joiner
        self.ZERO_WIDTH_JOINER = '\u200D'  # Zero Width Joiner
        self.LEFT_TO_RIGHT_MARK = '\u200E'  # Left-to-Right Mark
        self.RIGHT_TO_LEFT_MARK = '\u200F'  # Right-to-Left Mark
        
        # Map binary digits to zero-width characters
        self.BINARY_TO_CHAR = {
            '0': self.ZERO_WIDTH_SPACE,
            '1': self.ZERO_WIDTH_NON_JOINER,
        }
        
        # Map zero-width characters back to binary
        self.CHAR_TO_BINARY = {
            self.ZERO_WIDTH_SPACE: '0',
            self.ZERO_WIDTH_NON_JOINER: '1',
        }
    
    def _int_to_bin(self, value: int, bits: int = 8) -> str:
        """Convert integer to binary string"""
        return format(value, f'0{bits}b')
    
    def _bin_to_int(self, binary: str) -> int:
        """Convert binary string to integer"""
        return int(binary, 2)
    
    def _text_to_binary(self, text: str) -> str:
        """Convert text to binary string"""
        return ''.join(self._int_to_bin(ord(char), 16) for char in text)  # 16 bits for Unicode
    
    def _binary_to_text(self, binary: str) -> str:
        """Convert binary string to text"""
        text = ""
        for i in range(0, len(binary), 16):
            if i + 16 <= len(binary):
                char_code = self._bin_to_int(binary[i:i+16])
                try:
                    text += chr(char_code)
                except ValueError:
                    break
        return text
    
    def encode(self, cover_text: str, secret_text: str, password: str) -> str:
        """
        Encode secret text into cover text using zero-width Unicode characters
        
        Args:
            cover_text: Cover text to hide data in
            secret_text: Secret text to hide
            password: Password for encryption
            
        Returns:
            str: Text with hidden secret data
        """
        try:
            # Encrypt secret text
            secret_bytes = secret_text.encode('utf-8')
            encrypted_data = encrypt_data(secret_bytes, password)
            
            # Convert encrypted data to binary
            binary_data = ''.join(self._int_to_bin(byte) for byte in encrypted_data)
            
            # Add length header (32 bits) + encrypted data
            length_binary = ''.join(self._int_to_bin(byte) for byte in len(encrypted_data).to_bytes(4, 'big'))
            full_binary = length_binary + binary_data
            
            # Add end marker (32 bits of 1s)
            full_binary += '1' * 32
            
            # Encode binary as zero-width characters
            encoded_chars = ''.join(self.BINARY_TO_CHAR[bit] for bit in full_binary)
            
            # Insert zero-width characters into cover text
            # Insert at the end to avoid disrupting the visible text
            stego_text = cover_text + encoded_chars
            
            return stego_text
            
        except Exception as e:
            print(f"Encoding failed: {str(e)}")
            raise ValueError(f"Failed to encode text: {str(e)}")
    
    def decode(self, stego_text: str, password: str) -> Optional[str]:
        """
        Decode secret text from stego text

        Args:
            stego_text: Text containing hidden data
            password: Password for decryption

        Returns:
            str: Extracted secret text or None if failed
        """
        try:
            # Extract zero-width characters from text
            encoded_chars = ""
            for char in stego_text:
                if char in self.CHAR_TO_BINARY:
                    encoded_chars += char

            if not encoded_chars:
                raise ValueError("No steganography data found in text")

            # Convert zero-width characters back to binary
            binary_data = ''.join(self.CHAR_TO_BINARY[char] for char in encoded_chars)

            # Find and remove end marker
            end_marker = '1' * 32
            if len(binary_data) < 32 or binary_data[-32:] != end_marker:
                raise ValueError("Invalid stego data: end marker not found")

            binary_data = binary_data[:-32]

            # Extract length header (32 bits = 4 bytes)
            if len(binary_data) < 32:
                raise ValueError("Invalid stego data: insufficient bytes")

            length_binary = binary_data[:32]
            length_bytes = bytearray()
            for i in range(0, 32, 8):
                byte_binary = length_binary[i:i+8]
                length_bytes.append(self._bin_to_int(byte_binary))

            data_length = int.from_bytes(bytes(length_bytes), 'big')

            # Extract encrypted data
            if len(binary_data) < 32 + (data_length * 8):
                raise ValueError("Invalid stego data: corrupted length header")

            encrypted_binary = binary_data[32:32 + (data_length * 8)]
            encrypted_bytes = bytearray()
            for i in range(0, len(encrypted_binary), 8):
                byte_binary = encrypted_binary[i:i+8]
                encrypted_bytes.append(self._bin_to_int(byte_binary))

            encrypted_data = bytes(encrypted_bytes)

            # Decrypt data
            decrypted_data = decrypt_data(encrypted_data, password)

            # Convert to text
            secret_text = decrypted_data.decode('utf-8')

            return secret_text

        except Exception as e:
            print(f"Decoding failed: {str(e)}")
            return None
    
    def validate_text(self, text: str) -> Tuple[bool, str]:
        """
        Validate if text is suitable for steganography
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not text or len(text.strip()) == 0:
                return False, "Text cannot be empty"
            
            if len(text) < 10:
                return False, "Cover text too short. Minimum 10 characters required"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid text: {str(e)}"















