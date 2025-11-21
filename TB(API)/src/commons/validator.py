# validator.py
from src.constants.constants import Constants
from src.constants.global_data import GlobalData
from src.exceptions.db_exception import DBException
from src.exceptions.validation_exception import ValidationException
from src.utils.db_utils import db_connect
from src.commons.config_manager import cfg
from src.utils.encryption_utils import decrypt
from src.utils.logger import Logger

logger = Logger.get_logger()


async def validate_db_connection():
    """
    Validate DB connection, preload table schemas, and verify column structure.
    """
    try:
        db_env = cfg.get_env_config(Constants.DATABASE)
        local_table_name = decrypt(cfg.get_value_config(db_env, Constants.TABLE_NAME))
        logger.info(f"Validating DB connection for table: {local_table_name}")

        tables_to_load = [
            "user",
            "conversation",
            "conversation_participants",
            "messages",
            "receipts",
        ]

        for table in tables_to_load:
            try:
                await db_connect.set_up_table(table)
                logger.info(f"Loaded table: {table}")
            except Exception as e:
                logger.error(f"Failed to load table: {table} | Error: {e}")
                raise DBException(f"Failed to load table: {table} | Error: {e}")

        GlobalData.TABLE_NAME = local_table_name
        logger.info(f"DB validated successfully for table: {local_table_name}")

    except Exception as e:
        logger.error(f"DB validation failed: {e}")
        raise


def validate_jwt_data(params):
    """Validate JWT payload structure."""
    try:
        if not isinstance(params, dict):
            raise ValidationException("Parameters payload must be a JSON object.")

        if len(Constants.JWT_PARAM_LOAD) != len(params):
            GlobalData.STATUS_CODE = Constants.JWT_PARAM_ERROR
            raise ValidationException("Incorrect number of JWT parameters.")

        missing = Constants.JWT_PARAM_LOAD - set(params.keys())
        if missing:
            raise ValidationException(f"Missing JWT parameters: {missing}")

    except Exception as e:
        logger.error(f"JWT validation failed: {e}")
        raise ValidationException(
            f"Invalid JWT parameters. || Error Code {Constants.JWT_PARAM_ERROR}"
        )


def validate_conversation_data(params):
    """Validate conversation creation request payload."""
    try:
        if not isinstance(params, dict):
            raise ValidationException("Payload must be a JSON object.")

        if len(Constants.CONVERSATION_PARAM_LOAD.intersection(params.keys())) != len(Constants.CONVERSATION_PARAM_LOAD):
            GlobalData.STATUS_CODE = Constants.CONVERSATION_PARAM_ERROR
            raise ValidationException("Missing or extra conversation parameters.")

        participants = params.get(Constants.CONVERSATION_PARAM_PARTICIPANTS)
        if not isinstance(participants, list) or not participants:
            raise ValidationException("Participants must be a non-empty list.")

        creator_email = params.get(Constants.CONVERSATION_PARAM_CREATED_BY)
        if not isinstance(creator_email, str) or "@" not in creator_email:
            raise ValidationException("Invalid creator email format.")

        conversation_type = params.get(Constants.CONVERSATION_PARAM_TYPE, Constants.CONVERSATION_TYPE_DIRECT)
        if conversation_type == Constants.CONVERSATION_TYPE_DIRECT and len(participants) != 1:
            raise ValidationException("Direct conversation must have exactly one participant.")

        for email in participants:
            if not isinstance(email, str) or "@" not in email:
                raise ValidationException(f"Invalid participant email: {email}")

        logger.info("Conversation payload validated successfully.")

    except Exception as e:
        logger.error(f"Conversation validation failed: {e}")
        raise ValidationException(
            f"Invalid Conversation parameters. || Error Code {Constants.CONVERSATION_PARAM_ERROR}"
        )

def validate_forgot_pwd_data(params):
    """Validate forgot password request payload"""
    try:
        if not isinstance(params, dict):
            raise

        if len(Constants.FORGOT_PASSWORD_PARAM_LOAD) != len(params):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

        if len(Constants.FORGOT_PASSWORD_PARAM_LOAD.intersection(tuple(params.keys()))) != len(Constants.FORGOT_PASSWORD_PARAM_LOAD):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

    except Exception as e:
        raise ValidationException(
            f"The Input parameters are not as expected, kindly send correct parameters. "
            f"|| Error code {Constants.SIGNIN_PARAM_ERROR} Error : {str(e)}"
        )


def validate_update_pwd_data(params):
    """Validate reset password payload"""
    try:
        if not isinstance(params, dict):
            raise

        if len(Constants.UPDATE_PASSWORD_PARAM_LOAD) != len(params):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

        if len(Constants.UPDATE_PASSWORD_PARAM_LOAD.intersection(tuple(params.keys()))) != len(Constants.UPDATE_PASSWORD_PARAM_LOAD):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

    except Exception as e:
        raise ValidationException(
            f"The Input parameters are not as expected, kindly send correct parameters. "
            f"|| Error code {Constants.SIGNIN_PARAM_ERROR} Error : {str(e)}"
        )


def validate_otp_data(params):
    """Validate OTP request payload"""
    try:
        if not isinstance(params, dict):
            raise

        if len(Constants.OTP_VALIDATE_PARAM_LOAD) != len(params):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

        if len(Constants.OTP_VALIDATE_PARAM_LOAD.intersection(tuple(params.keys()))) != len(Constants.OTP_VALIDATE_PARAM_LOAD):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

    except Exception as e:
        raise ValidationException(
            f"The Input parameters are not as expected, kindly send correct parameters. "
            f"|| Error code {Constants.SIGNIN_PARAM_ERROR} Error : {str(e)}"
        )



def validate_signin_data(params):
    """Validate signin payload"""
    try:
        if not isinstance(params, dict):
            raise

        if len(Constants.SIGNIN_PARAM_LOAD) != len(params):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

        if len(Constants.SIGNIN_PARAM_LOAD.intersection(tuple(params.keys()))) != len(Constants.SIGNIN_PARAM_LOAD):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

    except Exception as e:
        raise ValidationException(
            f"The Input parameters are not as expected, kindly send correct parameters. "
            f"|| Error code {Constants.SIGNIN_PARAM_ERROR} Error : {str(e)}"
        )


def validate_signup_data(params):
    """Validate signup payload"""
    try:
        if not isinstance(params, dict):
            raise

        if len(Constants.SIGNUP_PARAM_LOAD) != len(params):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

        if len(Constants.SIGNUP_PARAM_LOAD.intersection(tuple(params.keys()))) != len(Constants.SIGNUP_PARAM_LOAD):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

    except Exception as e:
        raise ValidationException(
            f"The Input parameters are not as expected, kindly send correct parameters. "
            f"|| Error code {Constants.SIGNIN_PARAM_ERROR} Error : {str(e)}"
        )


def validate_profile_data(params):
    """Validate profile update payload"""
    try:
        if not isinstance(params, dict):
            raise

        if len(Constants.PROFILE_PARAM_LOAD) != len(params):
            GlobalData.STATUS_CODE = Constants.SIGNIN_PARAM_ERROR
            raise

        if len(Constants.PROFILE_PARAM_LOAD.intersection(tuple(params.keys()))) != len(Constants.PROFILE_PARAM_LOAD):
            GlobalData.STATUS_CODE = Constants.SIGNUP_PARAM_ERROR
            raise

    except Exception as e:
        raise ValidationException(
            f"The Input parameters are not as expected, kindly send correct parameters. "
            f"|| Error code {Constants.SIGNUP_PARAM_ERROR} Error : {str(e)}"
        )

