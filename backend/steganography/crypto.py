"""
AES encryption/decryption utilities for steganography
"""
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class AESCrypto:
    def __init__(self):
        self.key_size = 32  # 256 bits
        self.iv_size = 16   # 128 bits
    
    def derive_key(self, password: str, salt: bytes = None) -> bytes:
        """Derive a key from password using PBKDF2"""
        from Crypto.Protocol.KDF import PBKDF2
        
        if salt is None:
            salt = get_random_bytes(16)
        
        key = PBKDF2(password, salt, self.key_size, count=100000, hmac_hash_module=None)
        return key, salt
    
    def encrypt(self, data: bytes, password: str) -> bytes:
        """Encrypt data with AES-256-CBC"""
        # Derive key from password
        key, salt = self.derive_key(password)
        
        # Generate random IV
        iv = get_random_bytes(self.iv_size)
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Encrypt data
        padded_data = pad(data, AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        
        # Combine salt + iv + encrypted_data
        result = salt + iv + encrypted_data
        
        return result
    
    def decrypt(self, encrypted_data: bytes, password: str) -> bytes:
        """Decrypt data with AES-256-CBC"""
        try:
            # Extract components
            salt = encrypted_data[:16]
            iv = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]
            
            # Derive key from password
            key, _ = self.derive_key(password, salt)
            
            # Create cipher
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # Decrypt data
            decrypted_padded = cipher.decrypt(ciphertext)
            decrypted_data = unpad(decrypted_padded, AES.block_size)
            
            return decrypted_data
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


def encrypt_data(data: bytes, password: str) -> bytes:
    """Convenience function for encryption"""
    crypto = AESCrypto()
    return crypto.encrypt(data, password)


def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    """Convenience function for decryption"""
    crypto = AESCrypto()
    return crypto.decrypt(encrypted_data, password)




















