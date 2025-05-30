document.addEventListener('DOMContentLoaded', function () {
    const apiStatus = document.getElementById('api-status');
    const modelSelect = document.getElementById('model-select');
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearChatBtn = document.getElementById('clear-chat');
    
    // Add welcome message
    function addWelcomeMessage() {
        const welcomeMessage = `# Welcome to CodeAssist!

I'm your AI coding assistant, optimized to help with programming problems, explain concepts, and suggest efficient solutions.

## How I can help you:
- Write and optimize code in various languages
- Debug existing code and fix errors
- Explain programming concepts and algorithms
- Suggest best practices and patterns
- Refactor code for improved performance

Let me know what you're working on today!`;

        addMessage(welcomeMessage, false);
    }
    
    // Call this on page load
    addWelcomeMessage();
  
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'message user-message' : 'message bot-message';
        
        // Apply different processing based on whether it's a user or bot message
        if (isUser) {
            // For user messages, preserve layout but don't apply markdown processing
            const pre = document.createElement('pre');
            pre.className = 'user-input-pre';
            pre.textContent = message;
            messageDiv.appendChild(pre);
        } else {
            // Only process bot messages with markdown and syntax highlighting
            messageDiv.innerHTML = processMessageContent(message);
        }
        
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
  
    function processMessageContent(content) {
        // Configure marked options for better code highlighting and security
        marked.setOptions({
            breaks: true,
            gfm: true,
            pedantic: false,
            highlight: function(code, language) {
                // Escape HTML characters in code blocks
                code = code.replace(/[&<>"']/g, char => ({
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;'
                })[char]);
                
                if (language && hljs.getLanguage(language)) {
                    try {
                        return hljs.highlight(code, { language }).value;
                    } catch (err) {}
                }
                return hljs.highlightAuto(code).value;
            },
            sanitize: true // Enable built-in sanitizer
        });
        
        // Convert markdown to HTML
        const html = marked.parse(content);
        
        // Initialize syntax highlighting on all code blocks
        setTimeout(() => {
            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }, 0);
        
        return html;
    }
  
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message loading';
        loadingDiv.id = 'loading-indicator';
        loadingDiv.innerHTML = `
            <div class="loader"></div>
            <span>Thinking...</span>
        `;
        chatHistory.appendChild(loadingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
  
    function hideLoading() {
        const loadingDiv = document.getElementById('loading-indicator');
        if (loadingDiv) loadingDiv.remove();
    }
  
    // Add ability to press Tab in the textarea for indentation
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            
            // Get cursor position
            const start = this.selectionStart;
            const end = this.selectionEnd;
            
            // Insert tab at cursor position
            this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
            
            // Move cursor after the inserted tab
            this.selectionStart = this.selectionEnd = start + 4;
        }
    });
  
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        userInput.value = '';
        showLoading();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    model: modelSelect.value
                }),
                credentials: 'same-origin' // This helps manage cookies better
            });
  
            const data = await response.json();
            hideLoading();
            addMessage(data.response);
  
            if (data.usage) {
                const usageInfo = document.createElement('div');
                usageInfo.className = 'token-usage';
                usageInfo.textContent = `Model: ${data.usage.model} | Tokens: ${data.usage.total_tokens} (Prompt: ${data.usage.prompt_tokens}, Completion: ${data.usage.completion_tokens})`;
                chatHistory.appendChild(usageInfo);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
        } catch (error) {
            console.error('Error:', error);
            hideLoading();
            addMessage(`Error: Could not connect to the server. ${error.message}`);
        }
    }
  
    async function checkApiStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            apiStatus.className = data.valid ? 'status success' : 'status error';
            apiStatus.textContent = data.message;
        } catch (error) {
            console.error('Error checking API status:', error);
            apiStatus.className = 'status error';
            apiStatus.textContent = 'Error connecting to server';
        }
    }
  
    sendBtn.addEventListener('click', sendMessage);
  
    userInput.addEventListener('keydown', function (e) {
      // Send message on Enter (without Shift)
      if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault(); // Prevent default to avoid creating a new line
          sendMessage();
      }
      // Pressing Shift+Enter will create a new line (default textarea behavior)
    });
  
    clearChatBtn.addEventListener('click', async function () {
        try {
            await fetch('/api/clear-chat', {
                method: 'POST'
            });
  
            chatHistory.innerHTML = ''; // Clear all chat history
            addWelcomeMessage(); // Add welcome message again
        } catch (error) {
            console.error('Error:', error);
        }
    });
  
    // Add copy button to code blocks
    function addCopyButtonsToCodeBlocks() {
        document.querySelectorAll('pre code').forEach((codeBlock) => {
            if (!codeBlock.parentNode.querySelector('.copy-code-button')) {
                const button = document.createElement('button');
                button.className = 'copy-code-button';
                button.textContent = 'Copy';
                
                button.addEventListener('click', () => {
                    navigator.clipboard.writeText(codeBlock.textContent);
                    button.textContent = 'Copied!';
                    setTimeout(() => {
                        button.textContent = 'Copy';
                    }, 2000);
                });
                
                // Add position relative to pre for absolute positioning of button
                codeBlock.parentNode.style.position = 'relative';
                codeBlock.parentNode.appendChild(button);
            }
        });
    }
    
    // Add mutation observer to add copy buttons to new code blocks
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                addCopyButtonsToCodeBlocks();
            }
        });
    });
    
    observer.observe(chatHistory, { childList: true, subtree: true });
  
    // Check API status initially and every minute
    checkApiStatus();
    setInterval(checkApiStatus, 60000);
});
