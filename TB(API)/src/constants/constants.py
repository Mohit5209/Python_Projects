import os

class Constants:
    """
    This class contains the constants for the project
    """

    # Boolean
    FALSE_CONDITION = False
    TRUE_CONDITION = True
    YES = "yes"
    NO = "no"

    # Host/Port
    HOSTNAME = "HOSTNAME"
    PORT = "PORT"
    
    # Database
    SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
    SQLALCHEMY_ENGINE_OPTIONS = "SQLALCHEMY_ENGINE_OPTIONS"
    TABLE_META_DATA = "__table__"
    DB_USER = "DB_USER"
    DB_PASSWORD = "DB_PASSWORD"
    DATABASE = "DATABASE"
    DATABASE_NAME = "DATABASE_NAME"
    TABLE_NAME = "TABLE_NAME"
    DRIVER_NAME = "DB_DRIVER_NAME"
    DB_HOST = "DB_HOST"
    DB_PORT = "DB_PORT"
    POOL_RECYCLE = "POOL_RECYCLE"
    POOL_PRE_PING = "pool_pre_ping"
    ROOT_DIR_PATH = os.path.abspath(os.curdir)

    # API/Config
    DEFAULT_ENVIRONMENT = "DEFAULT"
    CONFIG_FILE_PATH = 'configuration/config.ini'

    # Params
    INPUT_PARAM_LEN = 3
    CHOICES = "choices"
    READ = "read"
    MESSAGE_KEY = "message"
    STATUS_CODE_KEY = 'status_code'
    USER_NAME_KEY = 'username'
    USER_EMAIL_KEY = "email"
    USERS_STRING = "users"
    RESPONSE_TEMPLATE = {STATUS_CODE_KEY: None, MESSAGE_KEY: None}

    # User Tables
    USER_TABLE = "user"
    CONVERSATION_TABLE = "conversation"
    CONVERSATION_PARTICIPANTS_TABLE = "conversation_participants"
    MESSAGE_TABLE = "messages"
    RECEIPTS_TABLE = "receipts"
    CONVERSATION_CLEARED_TABLE = "conversation_cleared"

    # Signin/Signup Params
    SIGNIN_PARAM_EMAIL = "email"
    SIGNIN_PARAM_PWD = "password"
    SIGNIN_PARAM_LOAD = {SIGNIN_PARAM_EMAIL, SIGNIN_PARAM_PWD}
    SIGNUP_PARAM_EMAIL = "email"
    SIGNUP_PARAM_PWD = "password"
    SIGNUP_PARAM_LOAD = {SIGNUP_PARAM_EMAIL, SIGNUP_PARAM_PWD}

    # Profile Params
    PROFILE_PARAM_EMAIL = SIGNUP_PARAM_EMAIL
    PROFILE_PARAM_FIRST_NAME = "first_name"
    PROFILE_PARAM_LAST_NAME = "last_name"
    PROFILE_PARAM_IMAGE = "profile_image"
    PROFILE_PARAM_LOAD = {
        PROFILE_PARAM_EMAIL,
        PROFILE_PARAM_FIRST_NAME,
        PROFILE_PARAM_LAST_NAME,
        PROFILE_PARAM_IMAGE,
    }

    # JWT Params
    JWT_PARAM_EMAIL = "email"
    JWT_PARAM_LOAD = {JWT_PARAM_EMAIL}
    JWT_TOKEN = "jwt_token"
    JWT_ENCRYPTION_ALGORITHM = "HS256"
    JWT_EXP_KEY = "exp"
    JWT_IAT_KEY = "iat"
    JWT_SUB_KEY = "sub"
    JWT_EXP_TIME_DAYS = 10

    # Forgot Password/OTP/Update Password Params
    FORGOT_PASSWORD_PARAM_EMAIL = "email"
    FORGOT_PASSWORD_PARAM_LOAD = {FORGOT_PASSWORD_PARAM_EMAIL}
    OTP_VALIDATE_PARAM_EMAIL = FORGOT_PASSWORD_PARAM_EMAIL
    OTP_VALIDATE_PARAM_OTP = "otp"
    OTP_VALIDATE_PARAM_LOAD = {OTP_VALIDATE_PARAM_EMAIL, OTP_VALIDATE_PARAM_OTP}
    UPDATE_PASSWORD_PARAM_EMAIL = FORGOT_PASSWORD_PARAM_EMAIL
    UPDATE_PASSWORD_PARAM_PASSWORD = "password"
    UPDATE_PASSWORD_PARAM_LOAD = {UPDATE_PASSWORD_PARAM_EMAIL, UPDATE_PASSWORD_PARAM_PASSWORD}

    # Misc
    ZERO = 0
    NONE = None
    MAX_BYTES = 10000000
    BACKUP_COUNT = 99
    ALL_PERMISSION = 0o777
    LOG_FILE_NAME = 'tb_signin_log-{}.txt'
    LOGGER_ROOT_FOLDER_NAME = 'log'
    EMPTY_STRING = ""
    DOT = '.'
    APPLICATION_USER = "APPLICATION"
    FIELD = "Field"
    UTF_8_ENCODING = "UTF-8"
    FORCE_TERMINATE = 1
    APP_SECRET_KEY = "YOUR JWT SECRET KEY HERE(base64 encoded)"

    # Methods
    METHOD_POST = 'POST'
    METHOD_GET = 'GET'
    METHOD_GET_POST = [METHOD_GET, METHOD_POST]

    # SQL Commands
    TEST_COMMAND_COLUMNS = "show COLUMNS FROM {}"
    TEST_COMMAND_TABLE = "show tables"
    SELECT_CONDITIONED = "SELECT {} FROM {} WHERE {} = '{}'"
    SELECT_CONDITIONED_AND = "SELECT {} FROM {} WHERE {} = '{}' and {} = '{}'"
    INSERT_COMMAND = "INSERT INTO {} ({}) VALUES ({})"
    UPDATE_COMMAND = "UPDATE {} SET {} WHERE {} = '{}'"

    # Syntax
    NULL_SYNTAX = "NULL"

    # Date/Time
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DOB_FORMAT = "%Y/%m/%d"

    # Database Column Lists
    UID = "uid"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    PASSWORD = "password"
    EMAIL = "email"
    CREATED_ON = "created_on"
    PROFILE_IMAGE = "profile_image"
    AUTH_INFO = "auth_info"
    
    USER_DATABASE_COLUMN_LIST = [
        UID, FIRST_NAME, LAST_NAME, PASSWORD, EMAIL, CREATED_ON, PROFILE_IMAGE, AUTH_INFO
    ]

    GROUP = "group"
    PRIVATE = "private"
    TEXT = "text"
    CREATED_AT = "created_at"
    SENT_BY_ME = "sent_by_me"
    LAST_MESSAGE = "last_message"
    UNREAD_COUNT = "unread_count"
    SENDER = "sender"
    SENT = "sent"
    DELIVERED = "delivered"
    SENDER_NAME = "sender_name"

    CONVERSATION_ID = "conversation_id"
    CONVERSATION_NAME = "conversation_name"
    CONVERSATION_TYPE = "conversation_type"
    CREATED_BY = "created_by"
    CONVERSATION_CREATED_ON = "created_on"
    IS_FAVORITE = "is_favorite"
    IS_PINNED = "is_pinned"

    CONVERSATION_DATABASE_COLUMN_LIST = [
        CONVERSATION_ID, CONVERSATION_NAME, CONVERSATION_TYPE, CREATED_BY, CONVERSATION_CREATED_ON , IS_FAVORITE, IS_PINNED
    ]

    MESSAGE_ID = "message_id"
    MESSAGE_CONVERSATION_ID = "conversation_id"
    MESSAGE_UID = "uid"
    BODY = "body"
    SENT_AT = "sent_at"

    MESSAGES_DATABASE_COLUMN_LIST = [
        MESSAGE_ID, MESSAGE_CONVERSATION_ID, MESSAGE_UID, BODY, SENT_AT
    ]

    RECEIPT_MESSAGE_ID = "message_id"
    RECEIPT_UID = "uid"
    STATUS = "status" 
    UPDATED_AT = "updated_at"

    RECEIPTS_DATABASE_COLUMN_LIST = [
        RECEIPT_MESSAGE_ID, RECEIPT_UID, STATUS, UPDATED_AT
    ]

    CONVERSATION_CLEARED_ID = "uid"
    CLEARED_CONVERSATION_ID = "conversation_id"
    CLEARED_AT = "cleared_at"
    CONVERSATION_CLEARED_DATABASE_COLUMN_LIST = [
        CONVERSATION_CLEARED_ID, CLEARED_CONVERSATION_ID, CLEARED_AT
    ]

    DEVICES_TABLE = "devices"

    ID = "id"
    UID = "uid"
    DEVICE_ID = "device_id"

    DEVICE_DATABASE_COLUMN_LIST = [
        ID, UID, DEVICE_ID
    ]
    # Success/Error Codes & Messages
    SUCCESS_CODE = 200
    INTERNAL_SERVER = 500
    DB_RETRIEVAL_ERROR = 401
    DB_CONNECTION_ERROR = 400
    DB_INSERTION_ERROR = 402
    TABLE_EXISTENCE_ERROR = 403
    FIELD_EXISTENCE_ERROR = 405
    SIGNIN_PARAM_ERROR = 406
    SIGNUP_PARAM_ERROR = 406
    USER_EXISTENCE_ERROR = 407
    USER_EXISTENCE_ERROR_MESSAGE = "User Doesn't Exists"
    USER_CREDENTIAL_ERROR = 408
    USER_CREDENTIAL_ERROR_MESSAGE = "Invalid Password"
    USER_SMTP_COMMUNICATION_ERROR = 409
    USER_SMTP_COMMUNICATION_ERROR_MESSAGE = "SMTP Communication Error"
    OTP_MISMATCH_ERROR = 410
    OTP_MISMATCH_ERROR_MESSAGE = "OTP does not match."
    BAD_REQUEST = 400
    JWT_PARAM_ERROR = 411
    JWT_ERROR_MESSAGE = "JWT Token Error"

    # Success Messages
    SIGNIN_SUCCESS_CODE_MESSAGE = "User Signin successful"
    SIGNUP_SUCCESS_CODE_MESSAGE = "User Signup successful"
    SIGNUP_PROFILE_API_SUCCESS_MESSAGE = "Profile Updated Successfully"
    SUCCESS_CODE_OTP_MESSAGE = "OTP Successfully Sent."
    SUCCESS_OTP_MATCH_MESSAGE = "OTP Validated."
    SUCCESS_UPDATE_PASSWORD_MESSAGE = "Password Updated Successfully."
    JWT_SUCCESS_CODE_MESSAGE = "JWT Token Created Successfully."
    APPLICATION_ERROR_MESSAGE = "Internal Error."
    USER_WEB_TOKEN_ERROR_MESSAGE = "Error in creation of Login Token"

    # Conversation Related
    CONVERSATION_PARAM_ERROR = 5011
    CONVERSATION_SUCCESS_MESSAGE = "Conversation created successfully"
    CONVERSATION_FETCH_SUCCESS_MESSAGE = "Conversations fetched successfully"
    CONVERSATION_FETCH_ERROR_MESSAGE = "Error fetching conversations"
    CONVERSATION_ERROR_MESSAGE = "Failed to create conversation"
    USER_NOT_PART_OF_THIS_CONVO = "User not part of this conversation."
    PROFILE_FETCH_SUCCESS_MESSAGE = "Profile fetched successfully"
    MESSAGE_FETCH_SUCCESS_MESSAGE = "Messages fetched successfully"
    ERROR_FETCHING_MESSAGES = "Error fetching messages"
    PROFILE_FETCH_ERROR_MESSAGE = "Error fetching profile"
    ADD_TO_FAVORITES_SUCCESS_MESSAGE = "Conversation added to favorites successfully"
    REMOVE_FROM_FAVORITES_SUCCESS_MESSAGE = "Conversation removed from favorites successfully"
    CREATED_BY_EMAIL = "created_by_email"
    PARTICIPANTS = "participants"
    CONVERSATION_TYPE_DIRECT = "direct"
    MISSING_CONVERSATION_FIELDS_MESSAGE = "Missing required fields: created_by_email or participants"
    MISSING_MESSAGE_FIELDS_MESSAGE = "Missing required fields: conversation_id, email or body"
    SEND_MESSAGE_WS_SUCCESS_MESSAGE = "Message sent successfully"
    SEND_MESSAGE_WS_ERROR_MESSAGE = "Error while sending message"
    USER_NOT_FOUND_MESSAGE = "User with email {} not found."
    CONVERSATION_PARTICIPANTS_ERROR = "No valid participants found."
    CHAT_CLEARED_SUCCESS_MESSAGE = "Chat cleared successfully."
    INVALID_REQUEST_PARAMETERS_MESSAGE = "Invalid request parameters."
    ADMIN = "admin"
    MEMBER = "member"
    CONVERSATIONS_STRING_LOWER = "conversations"
    FAVORITES_STRING_LOWER = "favorites"
    PINNED_STRING_LOWER = "pinned"
    PINNED_FETCH_SUCCESS_MESSAGE = "Pinned conversations fetched successfully"
    FAVORITES_FETCH_SUCCESS_MESSAGE = "Favorite conversations fetched successfully"
    ADD_TO_PINNED_SUCCESS_MESSAGE = "Conversation pinned successfully"
    REMOVE_FROM_PINNED_SUCCESS_MESSAGE = "Conversation unpinned successfully"
    DEVICE_ADDED_SUCCESS = "Device added successfully."
    DEVICE_UPDATED_SUCCESS = "Device updated successfully."
    DEVICE_DELETED_SUCCESS = "Device deleted successfully."
    DEVICE_FETCH_SUCCESS = "Device details fetched successfully."
    DEVICE_ADD_ERROR = "Error adding device."
    DEVICE_UPDATE_ERROR = "Error updating device."
    DEVICE_DELETE_ERROR = "Error deleting device."
    DEVICE_FETCH_ERROR = "Error fetching device details."
    DEVICE_NOT_FOUND_ERROR = "Device not found."
    DEVICE_ALREADY_EXISTS_ERROR = "Device already exists."

    FCM_URL = "https://fcm.googleapis.com/fcm/send"

    # Email/OTP
    OTP_NUMBER_OF_DIGITS = 4
    EMAIL_SUBJECT = "Subject"
    EMAIL_FROM = "From"
    EMAIL_TO = "To"
    EMAIL_SMTP_SERVER_ADDRESS = "smtp.gmail.com"
    EMAIL_SMTP_SERVER_PORT = 465
    SENDER_EMAIL = "YOUR SENDER EMAIL HERE(base64 encoded)"
    SENDER_EMAIL_PASSWORD = "YOUR SENDER EMAIL PASSWORD HERE(base64 encoded)"
    AUTH_EMAIL_SUBJECT = "One-Time Password (OTP) Verification"
    FCM_SERVER_KEY = "YOUR FCM SERVER KEY HERE"
    EMAIL_BODY = """YOUR EMAIL BODY HERE"""

    # Conversation API Params
    CONVERSATION_PARAM_CREATED_BY = "created_by_email"
    CONVERSATION_PARAM_PARTICIPANTS = "participants"
    CONVERSATION_PARAM_NAME = "conversation_name"
    CONVERSATION_PARAM_TYPE = "conversation_type"
    CONVERSATION_PARAM_LOAD = {
        CONVERSATION_PARAM_CREATED_BY,
        CONVERSATION_PARAM_PARTICIPANTS
    }