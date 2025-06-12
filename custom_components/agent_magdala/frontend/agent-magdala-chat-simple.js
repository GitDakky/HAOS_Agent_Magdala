/**
 * Agent Magdala Simple Chat Card
 * Simplified version for better compatibility
 */

console.log('Loading Agent Magdala Simple Chat Card...');

class AgentMagdalaSimpleChatCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    console.log('Agent Magdala Simple Chat Card constructor called');
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
    console.log('Rendering Agent Magdala Simple Chat Card');
    
    this.shadowRoot.innerHTML = `
      <style>
        .chat-container {
          border: 1px solid #333;
          border-radius: 8px;
          padding: 16px;
          background: #1a1a1a;
          color: #ffffff;
          font-family: 'Roboto', sans-serif;
          height: 400px;
          display: flex;
          flex-direction: column;
        }
        .chat-header {
          background: #00ff41;
          color: #000;
          padding: 12px;
          border-radius: 4px;
          margin-bottom: 16px;
          font-weight: bold;
        }
        .chat-messages {
          flex: 1;
          overflow-y: auto;
          border: 1px solid #333;
          padding: 8px;
          margin-bottom: 16px;
          background: #0a0a0a;
        }
        .chat-input {
          display: flex;
          gap: 8px;
        }
        .chat-input input {
          flex: 1;
          padding: 8px;
          border: 1px solid #333;
          border-radius: 4px;
          background: #2a2a2a;
          color: #ffffff;
        }
        .chat-input button {
          padding: 8px 16px;
          background: #00ff41;
          color: #000;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: bold;
        }
        .message {
          margin-bottom: 8px;
          padding: 8px;
          border-radius: 4px;
        }
        .user-message {
          background: #00ff41;
          color: #000;
          text-align: right;
        }
        .agent-message {
          background: #333;
          color: #ffffff;
        }
      </style>
      <div class="chat-container">
        <div class="chat-header">${this.config.title || '🤖 Agent Magdala Guardian'}</div>
        <div class="chat-messages" id="messages">
          <div class="message agent-message">
            Hello! I'm Agent Magdala. This is the simple chat interface. Type a message below to test the connection.
          </div>
        </div>
        <div class="chat-input">
          <input type="text" id="messageInput" placeholder="Type your message...">
          <button id="sendButton">Send</button>
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
      if (e.key === 'Enter') {
        this.sendMessage();
      }
    });
  }

  async sendMessage() {
    const input = this.shadowRoot.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;

    this.addMessage(message, 'user');
    input.value = '';

    try {
      if (this.hass && this.hass.callService) {
        await this.hass.callService('agent_magdala', 'ask', {
          prompt: message,
          conversation_id: `simple_chat_${Date.now()}`
        });
        
        this.addMessage('Message sent to Agent Magdala! Check the Home Assistant logs for the response.', 'agent');
      } else {
        this.addMessage('Home Assistant connection not available. Please refresh the page.', 'agent');
      }
    } catch (error) {
      console.error('Chat error:', error);
      this.addMessage(`Error: ${error.message || 'Failed to send message'}`, 'agent');
    }
  }

  addMessage(text, sender) {
    const messagesContainer = this.shadowRoot.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  getCardSize() {
    return 3;
  }
}

// Define the custom element
customElements.define('agent-magdala-simple-chat', AgentMagdalaSimpleChatCard);

// Register with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'agent-magdala-simple-chat',
  name: 'Agent Magdala Simple Chat',
  description: 'Simple chat interface for Agent Magdala Guardian'
});

console.log('Agent Magdala Simple Chat Card registered successfully');
