import datetime
import jwt
from src.constants.constants import Constants

def create_jwt(user_email, secret_key):
    """
    Function to create JWT token from name and email
    """
    try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        exp_utc = now_utc + datetime.timedelta(days=Constants.JWT_EXP_TIME_DAYS)
        payload = {
            Constants.JWT_EXP_KEY: int(exp_utc.timestamp()),
            Constants.JWT_IAT_KEY: int(now_utc.timestamp()),
            Constants.JWT_SUB_KEY: user_email
        }
        user_jwt = jwt.encode(
            payload=payload,
            key=secret_key,
            algorithm=Constants.JWT_ENCRYPTION_ALGORITHM
        )
        return user_jwt
    except Exception:
        return None