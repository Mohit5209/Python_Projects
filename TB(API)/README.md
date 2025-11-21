# TB API

## Table of Contents
- [Description](#description)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Parameters](#parameters)
- [Usage](#usage)
- [Terminating Code](#terminating-code)
- [Directory Structure](#directory-structure)

---

## Description

This project implements a FastAPI for user management, authentication, and profile operations. It provides a robust set of endpoints for user registration, authentication, password management, and profile handling. Built with FastAPI and SQLAlchemy for efficient database operations.

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- MySQL or compatible database server

### Installation

```sh
git clone <repository-url>
cd backend_wind/user_api
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
   ```

### Configuration

Edit `configuration/config.ini` to set your database and server parameters. All parameters are base64 encoded except HOSTNAME, PORT and DATABASE.

### Parameters:
```ini
HOSTNAME:
    Level of API exposure on the system IP.
PORT:
    PORT on which the API will be exposed.
DATABASE: 
    Section of the database in the config file.
DB_USER:
    Username for the Database.
DB_PASSWORD:
    Password of the Database. 
DATABASE_NAME:
    Name of the Database for accessing entries.
TABLE_NAME:
    Name of the table for user data.
DB_DRIVER_NAME:
    Driver specifying the kind of database used.
DB_HOST:
    Host of the database.
POOL_RECYCLE:
    Prevents pool from using a connection past a certain age.
   ```

---

## Usage

Start the FastAPI server:

```sh
python app.py
```

The API will be available at `http://localhost:8000` by default.

## API Endpoints

### 1. Forgot Password
**POST** `/api/user/forgot-password`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Description:**  
Sends an OTP to the user's email for password reset.

---

### 2. OTP Validation
**POST** `/api/user/otp_validate`

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "1234"
}
```
**Description:**  
Validates the OTP sent to the user's email.

---

### 3. Reset Password
**POST** `/api/user/reset-password`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "newpassword"
}
```
**Description:**  
Resets the user's password after OTP validation.

---

### 4. Sign In
**POST** `/api/user/signin`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```
**Description:**  
Authenticates the user and returns a JWT token.

---

### 5. Sign Up
**POST** `/api/user/signup`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```
**Description:**  
Registers a new user.

---

### 6. Update Profile
**POST** `/api/user/profile`

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile_image": "https://example.com/image.jpg"
}
```
**Description:**  
Updates the user's profile information.

---

### 7. Generate JWT
**POST** `/api/user/generate_jwt`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Description:**  
Generates a JWT token for the user.

---

### 8. Get Direct Users
**POST** `/api/user/get_direct_users`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Description:**  
Fetches connected users (email, first_name, last_name) for the requester.

---

### 9. Get All Users
**POST** `/api/user/get_all_users`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Description:**  
Fetches all users except the requester.

---

### 10. Start Conversation
**POST** `/api/user/conversation_start`

**Request Body:**
```json
{
  "created_by_email": "creator@example.com",
  "participants": ["participant1@example.com", "participant2@example.com"],
  "conversation_name": "My Conversation",
  "conversation_type": "direct"
}
```
**Description:**  
Starts a new conversation with specified participants.

---

### 11. Get User Conversations
**POST** `/api/user/conversations`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Description:**  
Fetches all conversations for the user.

---

### 12. Send Message (WebSocket)
**WebSocket** `/api/user/send_message_ws/{conversation_id}/{email}`

**Path Parameters:**
- `conversation_id`: ID of the conversation
- `email`: User's email address

**Message Format:**
```json
{
  "body": "Hello, this is a message"
}
```
**Description:**  
WebSocket endpoint for real-time message sending. The server will acknowledge with message metadata and broadcast delivered/read statuses.

---

### 13. Get Messages
**POST** `/api/user/get_messages`

**Request Body:**
```json
{
  "email": "user@example.com",
  "conversation_id": 123
}
```
**Description:**  
Fetches messages for the given conversation.

---

### 14. Mark Messages Read
**POST** `/api/user/message_read`

**Request Body:**
```json
{
  "email": "user@example.com",
  "conversation_id": 123
}
```
**Description:**  
Marks unread messages in a conversation as read for the requester.

---

### 15. Clear Chat
**POST** `/api/user/clear_chat`

**Request Body:**
```json
{
  "email": "user@example.com",
  "conversation_id": 123
}
```
**Description:**  
Clears the chat for the given user/conversation.

---

### 16. Favorites & Pinned

#### 16.1 Add to Favorites
**POST** `/api/user/add_to_favorites`

**Request Body:**
```json
{
  "email": "user@example.com",
  "conversation_id": 123
}
```

#### 16.2 Remove from Favorites
**POST** `/api/user/remove_from_favorites`

**Request Body:**
```json
{
  "email": "user@example.com",
  "conversation_id": 123
}
```

#### 16.3 List Favorites
**POST** `/api/user/list_favorites`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### 16.4 Add to Pinned
**POST** `/api/user/add_to_pinned`

**Request Body:**
```json
{
  "email": "user@example.com",
  "conversation_id": 123
}
```

#### 16.5 Remove from Pinned
**POST** `/api/user/remove_from_pinned`

**Request Body:**
```json
{
  "email": "user@example.com",
  "conversation_id": 123
}
```

#### 16.6 List Pinned
**POST** `/api/user/list_pinned`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Description:**  
Endpoints for managing favorite and pinned conversations.

---

### 17. Group Participants
**POST** `/api/user/get_group_participants`

**Request Body:**
```json
{
  "conversation_id": 123
}
```
**Description:**  
Returns participant emails and display names for the group.

---

### 18. Device Management

#### 18.1 Register Device
**POST** `/api/user/register_device`

**Request Body:**
```json
{
  "email": "user@example.com",
  "device_id": "device-token-or-id"
}
```
**Description:**  
Registers a device ID for push notifications.

#### 18.2 Unregister Device
**POST** `/api/user/unregister_device`

**Request Body:**
```json
{
  "device_id": "device-token-or-id"
}
```
**Description:**  
Removes a previously registered device.

---

### 19. Check Favorite Status
**POST** `/api/user/is_favorite`

**Request Body:**
```json
{
  "email": "user@example.com",
  "conversation_id": 123
}
```
**Description:**  
Returns whether the specified conversation is favorited by the user.

---


## Terminating Code

To stop the server, press `Ctrl+C` in the terminal.

---

## Directory Structure

```
user_api/
├── app.py                    # Application entry point
├── configuration/            # Configuration files
│   └── config.ini            # Application configuration
├── requirements.txt          # Project dependencies
└── src/                      # Source code
    ├── app/
    │   ├── __init__.py
    │   └── urls.py           # API URL routing
    ├── commons/              # Common utilities and helpers
    │   ├── config_manager.py # Configuration management
    │   ├── email_auth.py     # Email authentication
    │   ├── fetch_response.py # Response handling
    │   ├── validator.py      # Data validation
    │   └── __init__.py
    ├── constants/            # Application constants and configurations
    │   ├── constants.py
    │   ├── global_data.py
    │   └── __init__.py
    ├── exceptions/           # Custom exceptions
    │   ├── base_exception.py
    │   ├── db_exception.py
    │   ├── encryption_utils_exception.py
    │   ├── FileFolder_exception.py
    │   ├── smtp_exception.py
    │   ├── validation_exception.py
    │   └── __init__.py
    └── utils/                # Utility functions
        ├── db_utils.py       # Database utilities
        ├── encryption_utils.py
        ├── jwt_utils.py      # JWT authentication
        ├── logger.py         # Logging configuration
        ├── pwd_utils.py      # Password utilities
        ├── send_notification.py # Notification handling
        ├── traceback_utils.py # Error tracing
        └── web_socket_utils.py # WebSocket utilities
```

