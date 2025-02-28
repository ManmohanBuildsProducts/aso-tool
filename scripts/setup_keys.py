from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from backend.utils.key_manager import generate_key, encrypt_api_key
import os

def setup_keys():
    # Generate encryption key
    encryption_key = generate_key()
    
    # DeepSeek API key
    api_key = "sk-340de15952f44634804e7ae35af95cd2"
    
    # Encrypt API key
    encrypted_key = encrypt_api_key(api_key, encryption_key)
    
    # Update .env file
    env_path = Path(__file__).parent.parent / 'backend' / '.env'
    
    # Read existing content
    existing_content = ""
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_content = f.read()
    
    # Add new keys if not present
    if 'ENCRYPTION_KEY' not in existing_content:
        with open(env_path, 'a') as f:
            f.write(f"\nENCRYPTION_KEY={encryption_key.decode()}\n")
    
    if 'DEEPSEEK_API_KEY_ENCRYPTED' not in existing_content:
        with open(env_path, 'a') as f:
            f.write(f"DEEPSEEK_API_KEY_ENCRYPTED={encrypted_key}\n")
    
    print("Keys setup completed!")

if __name__ == "__main__":
    setup_keys()