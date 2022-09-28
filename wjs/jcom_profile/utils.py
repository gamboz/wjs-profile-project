import base64
import hashlib


def generate_token(email: str):
    """
    Encode user's email, which is unique, in a token.
    The email is encoded using utf-8, hashed with sha-256 algorithm, encoded using Base64, and then it is returned as a
    string.
    :param email: The user email
    :return: The token as a string
    """
    return base64.b64encode(hashlib.sha256(email.encode('utf-8')).digest()).hex()
