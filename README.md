# Python Projects

This repository contains a collection of Python projects, primarily focusing on backend services and APIs.

## Projects

### 1. Bakasur Chat API
A REST API backend for the Bakasur Chat App, powered by Google's Gemini AI. This API provides the AI chat functionality used in the Bakasur Chat App.

> **Note:** The Flutter frontend for this API is maintained in the [Flutter_Projects/bakasur(ChatBot)](https://github.com/Mohit5209/Flutter_Projects/tree/main/bakasur(ChatBot)) directory.

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

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Python_Projects
```

2. Navigate to the desired project directory:
```bash
cd bakasur(API)  # For Bakasur Chat API
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