import hashlib

from src.constants.constants import Constants
from src.utils.encryption_utils import decrypt


def create_password(input_password, secret_key):
    """
    Function to create hashed password from string
    """
    hash = input_password.encode(Constants.UTF_8_ENCODING) + decrypt(secret_key).encode(Constants.UTF_8_ENCODING)

    hash = hashlib.sha3_512(hash)
    hashed_password = hash.hexdigest()
    return hashed_password