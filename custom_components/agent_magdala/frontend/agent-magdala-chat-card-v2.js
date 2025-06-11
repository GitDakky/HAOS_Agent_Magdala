/**
 * Agent Magdala Chat Card v2.0
 * Professional WebSocket-enabled chat interface for Agent Magdala Guardian
 */

class AgentMagdalaChatCardV2 extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.hass = null;
    this.conversationId = `chat_${Date.now()}`;
    this.isTyping = false;
  }

  set hass(hass) {
    this._hass = hass;
  }

  get hass() {
    return this._hass;
  }

  setConfig(config) {
    this.config = config;
    this.render();
  }

  render() {
    const theme = this.config.theme || 'dark';
    const height = this.config.height || '500px';
    
    this.shadowRoot.innerHTML = `
      <style>
        .chat-container {
          border: 1px solid ${theme === 'dark' ? '#333' : '#ddd'};
          border-radius: 12px;
          padding: 0;
          background: ${theme === 'dark' ? '#1a1a1a' : '#ffffff'};
          height: ${height};
          display: flex;
          flex-direction: column;
          font-family: 'Roboto', sans-serif;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .chat-header {
          background: ${theme === 'dark' ? '#00ff41' : '#2196F3'};
          color: ${theme === 'dark' ? '#000' : '#fff'};
          padding: 16px;
          font-size: 18px;
          font-weight: bold;
          border-radius: 12px 12px 0 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: #4CAF50;
          animation: pulse 2s infinite;
        }
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          background: ${theme === 'dark' ? '#0a0a0a' : '#f5f5f5'};
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .chat-input-container {
          padding: 16px;
          background: ${theme === 'dark' ? '#1a1a1a' : '#ffffff'};
          border-top: 1px solid ${theme === 'dark' ? '#333' : '#ddd'};
          border-radius: 0 0 12px 12px;
        }
        .chat-input {
          display: flex;
          gap: 12px;
          align-items: center;
        }
        .chat-input input {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid ${theme === 'dark' ? '#333' : '#ddd'};
          border-radius: 24px;
          background: ${theme === 'dark' ? '#2a2a2a' : '#ffffff'};
          color: ${theme === 'dark' ? '#ffffff' : '#000000'};
          font-size: 14px;
          outline: none;
          transition: border-color 0.3s;
        }
        .chat-input input:focus {
          border-color: ${theme === 'dark' ? '#00ff41' : '#2196F3'};
        }
        .chat-input button {
          padding: 12px 20px;
          background: ${theme === 'dark' ? '#00ff41' : '#2196F3'};
          color: ${theme === 'dark' ? '#000' : '#fff'};
          border: none;
          border-radius: 24px;
          cursor: pointer;
          font-weight: bold;
          transition: all 0.3s;
          min-width: 80px;
        }
        .chat-input button:hover {
          background: ${theme === 'dark' ? '#00cc33' : '#1976D2'};
          transform: translateY(-1px);
        }
        .chat-input button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }
        .message {
          max-width: 80%;
          padding: 12px 16px;
          border-radius: 18px;
          font-size: 14px;
          line-height: 1.4;
          word-wrap: break-word;
          animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .user-message {
          background: ${theme === 'dark' ? '#00ff41' : '#2196F3'};
          color: ${theme === 'dark' ? '#000' : '#fff'};
          align-self: flex-end;
          border-bottom-right-radius: 4px;
        }
        .agent-message {
          background: ${theme === 'dark' ? '#333' : '#e3f2fd'};
          color: ${theme === 'dark' ? '#ffffff' : '#000000'};
          align-self: flex-start;
          border-bottom-left-radius: 4px;
        }
        .typing-indicator {
          background: ${theme === 'dark' ? '#333' : '#e3f2fd'};
          color: ${theme === 'dark' ? '#ffffff' : '#000000'};
          align-self: flex-start;
          border-bottom-left-radius: 4px;
          padding: 12px 16px;
          border-radius: 18px;
          max-width: 80px;
        }
        .typing-dots {
          display: flex;
          gap: 4px;
        }
        .typing-dots span {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: ${theme === 'dark' ? '#00ff41' : '#2196F3'};
          animation: typing 1.4s infinite ease-in-out;
        }
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes typing {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }
        .timestamp {
          font-size: 11px;
          opacity: 0.7;
          margin-top: 4px;
        }
        .error-message {
          background: #f44336;
          color: white;
          align-self: center;
          text-align: center;
          font-size: 12px;
        }
      </style>
      <div class="chat-container">
        <div class="chat-header">
          <span>${this.config.title || '🤖 Agent Magdala Guardian'}</span>
          <div class="status-indicator" id="statusIndicator"></div>
        </div>
        <div class="chat-messages" id="messages">
          <div class="message agent-message">
            Hello! I'm Agent Magdala, your AI Guardian. I can help you monitor and control your smart home. What would you like to know?
          </div>
        </div>
        <div class="chat-input-container">
          <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Ask me about your home...">
            <button id="sendButton">Send</button>
          </div>
        </div>
      </div>
    `;

    this.setupEventListeners();
  }

  setupEventListeners() {
    const input = this.shadowRoot.getElementById('messageInput');
    const button = this.shadowRoot.getElementById('sendButton');

    button.addEventListener('click', () => this.sendMessage());
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
  }

  async sendMessage() {
    const input = this.shadowRoot.getElementById('messageInput');
    const button = this.shadowRoot.getElementById('sendButton');
    const message = input.value.trim();
    
    if (!message || this.isTyping) return;

    // Add user message
    this.addMessage(message, 'user');
    input.value = '';
    
    // Disable input while processing
    button.disabled = true;
    button.textContent = 'Sending...';
    this.isTyping = true;
    
    // Show typing indicator
    this.showTypingIndicator();

    try {
      if (this.hass && this.hass.callWS) {
        // Try WebSocket first
        const response = await this.hass.callWS({
          type: 'agent_magdala/chat',
          message: message,
          conversation_id: this.conversationId
        });

        this.hideTypingIndicator();
        
        if (response.result && response.result.response) {
          this.addMessage(response.result.response, 'agent');
        } else {
          this.addMessage('I received your message but had trouble responding. Please try again.', 'agent');
        }
      } else if (this.hass && this.hass.callService) {
        // Fallback to service call
        await this.hass.callService('agent_magdala', 'ask', {
          prompt: message,
          conversation_id: this.conversationId
        });
        
        this.hideTypingIndicator();
        this.addMessage('Message sent! The response will appear in Home Assistant events.', 'agent');
      } else {
        this.hideTypingIndicator();
        this.addMessage('Home Assistant connection not available. Please refresh the page.', 'error');
      }
    } catch (error) {
      this.hideTypingIndicator();
      console.error('Chat error:', error);
      this.addMessage(`Error: ${error.message || 'Failed to send message'}`, 'error');
    } finally {
      // Re-enable input
      button.disabled = false;
      button.textContent = 'Send';
      this.isTyping = false;
      input.focus();
    }
  }

  showTypingIndicator() {
    const messagesContainer = this.shadowRoot.getElementById('messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
      <div class="typing-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  hideTypingIndicator() {
    const typingIndicator = this.shadowRoot.getElementById('typingIndicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  addMessage(text, sender) {
    const messagesContainer = this.shadowRoot.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const now = new Date();
    const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
      <div>${text}</div>
      <div class="timestamp">${timestamp}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  getCardSize() {
    return 4;
  }
}

customElements.define('agent-magdala-chat-card-v2', AgentMagdalaChatCardV2);

// Register the card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'agent-magdala-chat-card-v2',
  name: 'Agent Magdala Chat Card v2',
  description: 'Professional WebSocket-enabled chat interface for Agent Magdala Guardian',
  preview: true
});
