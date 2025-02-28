from cryptography.fernet import Fernet
import base64
import os
from pathlib import Path

def generate_key():
    """Generate a key and save it to a file"""
    key = Fernet.generate_key()
    return key

def encrypt_api_key(api_key: str, encryption_key: bytes) -> str:
    """Encrypt the API key"""
    f = Fernet(encryption_key)
    encrypted_key = f.encrypt(api_key.encode())
    return base64.b64encode(encrypted_key).decode()

def decrypt_api_key(encrypted_key: str, encryption_key: bytes) -> str:
    """Decrypt the API key"""
    try:
        f = Fernet(encryption_key)
        decoded = base64.b64decode(encrypted_key)
        decrypted_key = f.decrypt(decoded)
        return decrypted_key.decode()
    except Exception as e:
        print(f"Error decrypting key: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Generate a new key
    key = generate_key()
    print(f"Generated key: {key}")
    
    # Example API key
    api_key = "sk-340de15952f44634804e7ae35af95cd2"
    
    # Encrypt
    encrypted = encrypt_api_key(api_key, key)
    print(f"Encrypted: {encrypted}")
    
    # Decrypt
    decrypted = decrypt_api_key(encrypted, key)
    print(f"Decrypted: {decrypted}")
    print(f"Matches original: {decrypted == api_key}")