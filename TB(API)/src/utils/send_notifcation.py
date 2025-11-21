import json
import httpx
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from logger import Logger
logger = Logger.get_logger()
SERVICE_ACCOUNT_FILE = "PATH TO YOUR FIREBASE PRIVATE SERVER KEY FOR PUSHING NOTIFICATION"
PROJECT_ID = "FIREBASE PROJECT ID"

def get_access_token():
    """Get OAuth2 access token for Firebase HTTP v1 API."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    credentials.refresh(Request())
    return credentials.token


async def send_device_notification(device_token: str, title: str, body: str):
    """Send FCM push notification using HTTP v1 API (async)."""
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8",
    }

    message = {
        "message": {
            "token": device_token,
            "notification": {
                "title": title,
                "body": body
            },
            "android": {
                "priority": "high"
            },
            "apns": {
                "headers": {"apns-priority": "10"}
            }
        }
    }

    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=json.dumps(message))

    if response.status_code == 200:
        logger.info(f"Notification sent successfully to {device_token}")
    else:
        logger.error(f"Failed to send notification ({response.status_code}): {response.text}")
