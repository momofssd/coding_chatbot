document.addEventListener('DOMContentLoaded', function () {
  const apiStatus = document.getElementById('api-status');
  const modelSelect = document.getElementById('model-select');
  const chatHistory = document.getElementById('chat-history');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const clearChatBtn = document.getElementById('clear-chat');

  function addMessage(message, isUser = false) {
      const messageDiv = document.createElement('div');
      messageDiv.className = isUser ? 'message user-message' : 'message bot-message';
      messageDiv.innerHTML = processMessageContent(message);
      chatHistory.appendChild(messageDiv);
      chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  function processMessageContent(content) {
    // Configure marked options
    marked.setOptions({
        breaks: true,
        highlight: function(code, language) {
            if (language && hljs.getLanguage(language)) {
                try {
                    return hljs.highlight(code, { language }).value;
                } catch (err) {}
            }
            return hljs.highlightAuto(code).value;
        }
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
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  message: message,
                  model: modelSelect.value
              })
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
    // Send message on Shift+Enter
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

          chatHistory.innerHTML = `
              <div class="message bot-message">
                  Chat cleared. How can I help you today?
              </div>
          `;
      } catch (error) {
          console.error('Error:', error);
      }
  });

  setInterval(checkApiStatus, 60000);
});

