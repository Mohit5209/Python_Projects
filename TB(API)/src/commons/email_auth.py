import smtplib
from email.mime.text import MIMEText
from random import randint

from src.constants.constants import Constants
from src.constants.global_data import GlobalData
from src.exceptions.smtp_exception import SMTPException
from src.utils.encryption_utils import decrypt


def send_email(email_user, otp_pin_value):
    """
    This method will send mail

    Raises:
        SMTPException: Exception during sending mail.
    """
    msg = MIMEText(Constants.EMAIL_BODY.format(otp_pin_value))
    msg[Constants.EMAIL_SUBJECT] = Constants.AUTH_EMAIL_SUBJECT
    msg[Constants.EMAIL_FROM] = Constants.EMAIL_FROM
    msg[Constants.EMAIL_TO] = ', '.join([email_user])

    try:
        with smtplib.SMTP_SSL(Constants.EMAIL_SMTP_SERVER_ADDRESS, Constants.EMAIL_SMTP_SERVER_PORT) as smtp_server:
            smtp_server.login(decrypt(Constants.SENDER_EMAIL),
                              decrypt(Constants.SENDER_EMAIL_PASSWORD))
            mail_status = smtp_server.sendmail(decrypt(Constants.SENDER_EMAIL),
                                               email_user, msg.as_string())

    except Exception as e:
        GlobalData.STATUS_CODE = Constants.USER_SMTP_COMMUNICATION_ERROR
        GlobalData.STATUS_MESSAGE = Constants.USER_SMTP_COMMUNICATION_ERROR_MESSAGE
        raise SMTPException("Issue while sending OTP mail.")


def pin_generator():
    """
    This method will generate a PIN of 6 digits
    """
    range_start = 10**(Constants.OTP_NUMBER_OF_DIGITS-1)
    range_end = (10**Constants.OTP_NUMBER_OF_DIGITS)-1
    return randint(range_start, range_end)
