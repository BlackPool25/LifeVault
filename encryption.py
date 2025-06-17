from cryptography.fernet import Fernet
import os

KEY_FILE = 'secret.key'

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

fernet = load_key()

def encrypt_data(data):
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data):
    return fernet.decrypt(data.encode()).decode()