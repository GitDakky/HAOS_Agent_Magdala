/**
 * Agent Magdala Chat Card
 * A custom Lovelace card for chatting with the AI Guardian Agent
 */

class AgentMagdalaChatCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.messages = [];
    this.conversationId = `conv_${Date.now()}`;
  }

  setConfig(config) {
    this.config = config;
    this.render();
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  render() {
    const title = this.config?.title || 'Agent Magdala Guardian';
    const theme = this.config?.theme || 'dark';
    
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .chat-card {
          background: ${theme === 'dark' ? '#1a1a1a' : '#ffffff'};
          border: 1px solid ${theme === 'dark' ? '#333' : '#e0e0e0'};
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          max-width: 100%;
          height: ${this.config?.height || '500px'};
          display: flex;
          flex-direction: column;
        }
        
        .chat-header {
          background: linear-gradient(135deg, #00ff41, #00cc33);
          color: #000;
          padding: 16px;
          font-weight: 600;
          font-size: 18px;
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .chat-header .icon {
          width: 24px;
          height: 24px;
          background: #000;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #00ff41;
          font-size: 14px;
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
        
        .message {
          max-width: 80%;
          padding: 12px 16px;
          border-radius: 18px;
          font-size: 14px;
          line-height: 1.4;
          word-wrap: break-word;
        }
        
        .message.user {
          align-self: flex-end;
          background: #00ff41;
          color: #000;
          border-bottom-right-radius: 6px;
        }
        
        .message.agent {
          align-self: flex-start;
          background: ${theme === 'dark' ? '#333' : '#e0e0e0'};
          color: ${theme === 'dark' ? '#fff' : '#000'};
          border-bottom-left-radius: 6px;
          border: 1px solid ${theme === 'dark' ? '#555' : '#ccc'};
        }
        
        .message.error {
          background: #ff0040;
          color: #fff;
          align-self: flex-start;
        }
        
        .message.system {
          align-self: center;
          background: ${theme === 'dark' ? '#444' : '#ddd'};
          color: ${theme === 'dark' ? '#ccc' : '#666'};
          font-style: italic;
          font-size: 12px;
          max-width: 90%;
        }
        
        .message-time {
          font-size: 10px;
          opacity: 0.7;
          margin-top: 4px;
        }
        
        .chat-input {
          padding: 16px;
          background: ${theme === 'dark' ? '#1a1a1a' : '#ffffff'};
          border-top: 1px solid ${theme === 'dark' ? '#333' : '#e0e0e0'};
          display: flex;
          gap: 12px;
          align-items: flex-end;
        }
        
        .input-field {
          flex: 1;
          background: ${theme === 'dark' ? '#333' : '#f0f0f0'};
          border: 1px solid ${theme === 'dark' ? '#555' : '#ccc'};
          border-radius: 20px;
          padding: 12px 16px;
          color: ${theme === 'dark' ? '#fff' : '#000'};
          font-size: 14px;
          resize: none;
          min-height: 20px;
          max-height: 100px;
          font-family: inherit;
        }
        
        .input-field:focus {
          outline: none;
          border-color: #00ff41;
          box-shadow: 0 0 0 2px rgba(0, 255, 65, 0.2);
        }
        
        .send-button {
          background: #00ff41;
          color: #000;
          border: none;
          border-radius: 50%;
          width: 44px;
          height: 44px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          transition: all 0.2s ease;
        }
        
        .send-button:hover {
          background: #00cc33;
          transform: scale(1.05);
        }
        
        .send-button:disabled {
          background: #666;
          cursor: not-allowed;
          transform: none;
        }
        
        .typing-indicator {
          display: none;
          align-self: flex-start;
          background: ${theme === 'dark' ? '#333' : '#e0e0e0'};
          color: ${theme === 'dark' ? '#fff' : '#000'};
          padding: 12px 16px;
          border-radius: 18px;
          border-bottom-left-radius: 6px;
          font-style: italic;
          opacity: 0.8;
        }
        
        .typing-indicator.show {
          display: block;
        }
        
        .status-bar {
          padding: 8px 16px;
          background: ${theme === 'dark' ? '#222' : '#f8f8f8'};
          border-top: 1px solid ${theme === 'dark' ? '#333' : '#e0e0e0'};
          font-size: 12px;
          color: ${theme === 'dark' ? '#888' : '#666'};
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .status-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
        }
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #00ff41;
        }
        
        .status-dot.offline {
          background: #ff0040;
        }
        
        /* Scrollbar styling */
        .chat-messages::-webkit-scrollbar {
          width: 6px;
        }
        
        .chat-messages::-webkit-scrollbar-track {
          background: transparent;
        }
        
        .chat-messages::-webkit-scrollbar-thumb {
          background: ${theme === 'dark' ? '#555' : '#ccc'};
          border-radius: 3px;
        }
        
        .chat-messages::-webkit-scrollbar-thumb:hover {
          background: ${theme === 'dark' ? '#666' : '#bbb'};
        }
      </style>
      
      <div class="chat-card">
        <div class="chat-header">
          <div class="icon">🤖</div>
          <span>${title}</span>
        </div>
        
        <div class="chat-messages" id="messages">
          <div class="message system">
            Guardian Agent Magdala is online and ready to assist you with your smart home.
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
          </div>
        </div>
        
        <div class="typing-indicator" id="typing">
          Agent is thinking...
        </div>
        
        <div class="chat-input">
          <textarea 
            class="input-field" 
            id="messageInput" 
            placeholder="Ask your Guardian Agent anything..."
            rows="1"
          ></textarea>
          <button class="send-button" id="sendButton">
            ➤
          </button>
        </div>
        
        <div class="status-bar">
          <div class="status-indicator">
            <div class="status-dot" id="statusDot"></div>
            <span id="statusText">Online</span>
          </div>
          <div id="conversationInfo">
            Conversation: ${this.conversationId.slice(-8)}
          </div>
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    const messageInput = this.shadowRoot.getElementById('messageInput');
    const sendButton = this.shadowRoot.getElementById('sendButton');
    
    // Send message on button click
    sendButton.addEventListener('click', () => this.sendMessage());
    
    // Send message on Enter (but allow Shift+Enter for new lines)
    messageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
      messageInput.style.height = 'auto';
      messageInput.style.height = Math.min(messageInput.scrollHeight, 100) + 'px';
    });
    
    // Listen for agent responses
    this.hass?.connection?.subscribeEvents((event) => {
      if (event.event_type === 'agent_magdala_response') {
        this.handleAgentResponse(event.data);
      }
    }, 'agent_magdala_response');
  }

  async sendMessage() {
    const messageInput = this.shadowRoot.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    this.addMessage(message, 'user');
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Show typing indicator
    this.showTyping(true);
    
    try {
      // Call the agent service
      await this.hass.callService('agent_magdala', 'ask', {
        prompt: message,
        conversation_id: this.conversationId
      });
    } catch (error) {
      this.showTyping(false);
      this.addMessage(`Error: ${error.message}`, 'error');
      this.updateStatus('offline', 'Error');
    }
  }

  handleAgentResponse(data) {
    this.showTyping(false);
    
    if (data.conversation_id === this.conversationId) {
      const messageType = data.error ? 'error' : 'agent';
      this.addMessage(data.response, messageType);
      this.updateStatus('online', 'Online');
    }
  }

  addMessage(text, type) {
    const messagesContainer = this.shadowRoot.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const time = new Date().toLocaleTimeString();
    messageDiv.innerHTML = `
      ${text}
      <div class="message-time">${time}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Store message
    this.messages.push({ text, type, time });
  }

  showTyping(show) {
    const typingIndicator = this.shadowRoot.getElementById('typing');
    typingIndicator.classList.toggle('show', show);
    
    if (show) {
      const messagesContainer = this.shadowRoot.getElementById('messages');
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  updateStatus(status, text) {
    const statusDot = this.shadowRoot.getElementById('statusDot');
    const statusText = this.shadowRoot.getElementById('statusText');
    
    statusDot.className = `status-dot ${status === 'offline' ? 'offline' : ''}`;
    statusText.textContent = text;
  }

  set hass(hass) {
    this._hass = hass;
  }

  get hass() {
    return this._hass;
  }

  getCardSize() {
    return 6; // Lovelace card size
  }
}

// Register the custom card
customElements.define('agent-magdala-chat-card', AgentMagdalaChatCard);

// Register with Lovelace
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'agent-magdala-chat-card',
  name: 'Agent Magdala Chat Card',
  description: 'Chat interface for Agent Magdala Guardian AI',
  preview: true,
  documentationURL: 'https://github.com/GitDakky/HAOS_Agent_Magdala'
});

console.info(
  '%c AGENT MAGDALA CHAT CARD %c v1.0.0 ',
  'color: white; background: #00ff41; font-weight: 700;',
  'color: #00ff41; background: black; font-weight: 700;'
);
