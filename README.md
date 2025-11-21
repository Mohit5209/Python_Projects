# Python Projects

This repository contains a collection of Python projects, primarily focusing on backend services and APIs.

## Quick Links

- **Bakasur Chat API**: [Folder](bakasur(API)/) · [README](bakasur(API)/README.md)
- **TB API**: [Folder](TB(API)/) · [README](TB(API)/README.md)

## Projects

### 1. Bakasur Chat API
A REST API backend for the Bakasur Chat App, powered by Google's Gemini AI. This API provides the AI chat functionality used in the Bakasur Chat App.

> **Note:** The Flutter frontend for this API is maintained in the [Flutter_Projects/bakasur](https://github.com/Mohit5209/Flutter_Projects/tree/main/bakasur) directory.

**Features:**
- RESTful API endpoints
- Integration with Google's Gemini AI
- Structured logging system
- Environment variable configuration
- Error handling and response formatting

**Setup:**
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export GEMINI_API_KEY='your-api-key-here'
export FLASK_HOST='0.0.0.0'  # Optional
export FLASK_PORT=5000      # Optional
```

3. Run the server:
```bash
python api.py
```

[View Bakasur Chat API README](bakasur(API)/README.md)

### 2. TB API
A production-ready FastAPI backend focused on user identity and messaging. It provides user registration and sign-in, JWT-based authentication, password reset via email OTP, profile management, and rich chat features including creating conversations (direct and group), sending/receiving messages, marking read status, favorites and pinned chats, and device registration for notifications. Real-time messaging is supported over WebSockets, and the service uses SQLAlchemy for database access with a clean, modular structure and centralized configuration.

**Highlights:**
- FastAPI with SQLAlchemy
- JWT auth, password reset via OTP
- Conversations, messages, favorites, pinned, and device registration
- WebSocket endpoint for real-time messaging

[View TB API README](TB(API)/README.md)

> **Note:** The Flutter frontend for this API is maintained in the [Flutter_Projects/tb_app](https://github.com/Mohit5209/Flutter_Projects/tree/main/tb_app) directory.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Python_Projects
```

2. Navigate to the desired project directory:
```bash
cd bakasur(API)  # For Bakasur Chat API
# or
cd TB(API)       # For TB API
```

3. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  
# On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit Pull Requests for any of the projects.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google's Gemini AI for the powerful language model
- The open-source community for their contributions
- Flask for the web framework
