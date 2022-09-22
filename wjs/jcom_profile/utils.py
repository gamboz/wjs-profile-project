import base64
import hashlib


def generate_token(email: str):
    return base64.b64encode(hashlib.sha256(email.encode('utf-8')).digest()).hex()
