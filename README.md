# Azure Coding ChatBot

A sophisticated AI-powered coding assistant that leverages Azure OpenAI's GPT models to provide intelligent programming help and code explanations.

## 🌟 Features

- Real-time AI coding assistance
- Support for multiple GPT models (GPT-4o Mini, GPT-4.1 Mini, GPT-4o)
- Syntax highlighting for code snippets
- Persistent conversation history
- Markdown rendering support
- Responsive web interface
- Docker containerization support

## 🔧 Technology Stack

### Backend
- **Python 3.x**
- **Flask**: Web framework for the backend API
- **Azure OpenAI SDK**: For interaction with Azure's GPT models
- **python-dotenv**: Environment variable management
- **Flask-CORS**: Cross-Origin Resource Sharing support

### Frontend
- **HTML5/CSS3**: Modern, responsive layout
- **JavaScript**: Client-side interactivity
- **highlight.js**: Code syntax highlighting
- **marked.js**: Markdown rendering
- **Font Awesome**: UI icons

### DevOps
- **Docker**: Application containerization
- **Environment Variables**: Secure configuration management

## 📁 Project Structure

```
AzureCodingChatBot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── static/
│   ├── css/
│   │   └── styles.css    # Application styling
│   └── js/
│       └── script.js     # Frontend JavaScript
└── templates/
    └── index.html        # Main HTML template
```

## 🔄 Process Flow

1. **Initialization**
   - Application loads and validates Azure OpenAI API key
   - Establishes connection with Azure OpenAI service
   - Initializes Flask web server

2. **User Interaction**
   - User sends a coding question through the web interface
   - Frontend validates and processes the input
   - Request is sent to backend API

3. **AI Processing**
   - Backend maintains conversation context
   - Sends formatted prompt to Azure OpenAI
   - Receives and processes AI response
   - Manages token usage and conversation history

4. **Response Handling**
   - AI response is formatted with proper markdown/code highlighting
   - Sent back to frontend for display
   - Conversation history is updated
   - Usage statistics are tracked

## 💡 Value Proposition

1. **Enhanced Productivity**
   - Instant access to coding expertise
   - Detailed explanations and examples
   - Best practices and optimization suggestions

2. **Learning Tool**
   - In-depth explanations of coding concepts
   - Real-time code analysis
   - Interactive learning experience

3. **Code Quality**
   - Suggestions for code improvements
   - Best practice implementations
   - Error handling recommendations

4. **Flexibility**
   - Support for multiple programming languages
   - Customizable AI models
   - Scalable architecture

## 🚀 Getting Started

1. Clone the repository
2. Create a `.env` file with your Azure OpenAI API key:
   ```
   AZURE_API_KEY=your_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python app.py
   ```
   Or using Docker:
   ```
   docker build -t azure-coding-chatbot .
   docker run -p 5000:5000 azure-coding-chatbot
   ```

## 🔒 Security Notes

- API keys are managed through environment variables
- Session-based conversation history
- CORS protection enabled
- Rate limiting on API endpoints
- Secure token management

## 🔄 Version
Current Version: 1.0.1
