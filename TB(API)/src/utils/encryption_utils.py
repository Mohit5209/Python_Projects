import base64
from src.exceptions.encryption_utils_exception import DecryptException


def decrypt(data):
    """
    Description: This function decrypts the encoded data.
    :return: decoded string
    """
    try:
        return (base64.b64decode(data)).decode('UTF-8')
    except Exception as e:
        raise DecryptException(
            "The data sent couldn't be decrypted exception occurred {}".format(e)) from e