# HAOS Agent Magdala - AI Guardian for Your Home

[![GitHub Release](https://img.shields.io/github/release/GitDakky/HAOS_Agent_Magdala.svg?style=for-the-badge)](https://github.com/GitDakky/HAOS_Agent_Magdala/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

An intelligent AI guardian agent for Home Assistant that proactively monitors your property, learns your family's patterns, and communicates through voice to keep your home secure, efficient, and comfortable.

## 🎯 Vision

Transform your Home Assistant into a **true AI guardian** that:
- **🛡️ Monitors** your property 24/7 through sensors and cameras
- **🧠 Learns** your family's routines and preferences with persistent memory
- **🗣️ Communicates** proactively via voice through your smart speakers
- **⚡ Acts** as your intelligent household companion and protector

## ✨ Guardian Features

### 🛡️ Security Guardian
- **Perimeter Monitoring**: Intelligent door/window/motion detection
- **Visitor Management**: Smart doorbell integration and guest announcements
- **Anomaly Detection**: Learns normal patterns, alerts on unusual activity
- **Emergency Response**: Automated alerts and emergency protocols

### 🏥 Wellness Guardian
- **Health Monitoring**: Medication reminders and wellness checks
- **Safety Alerts**: Environmental hazards (smoke, water, temperature)
- **Activity Tracking**: Monitors daily routines for elderly care
- **Emergency Detection**: Fall detection and medical alert integration

### ⚡ Energy Guardian
- **Smart Optimization**: Automated energy efficiency improvements
- **Usage Monitoring**: Tracks and reports energy consumption patterns
- **Cost Savings**: Schedules devices during off-peak hours
- **Waste Detection**: Alerts about forgotten lights and appliances

### 🧠 Intelligent Memory
- **Pattern Learning**: Understands your family's daily routines
- **Preference Storage**: Remembers temperature, lighting, and device preferences
- **Conversation History**: Maintains context across all interactions
- **Adaptive Behavior**: Continuously improves based on feedback

## 🚀 Technology Stack

- **🧠 Pydantic AI SDK**: Type-safe AI agent with structured validation
- **💾 Mem0**: Persistent memory system for learning and context
- **🗣️ Home Assistant TTS**: Local voice communication via smart speakers
- **🏠 Home Assistant Core**: Native integration with all your smart devices

## Prerequisites

- Home Assistant 2024.1.0 or newer
- OpenRouter API key (for AI model access)
- Mem0 API key (for persistent memory)
- Smart speakers or TTS-capable devices
- Sensors for monitoring (door/window, motion, temperature, etc.)

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/GitDakky/HAOS_Agent_Magdala` as a custom repository
5. Select "Integration" as the category
6. Click "Add"
7. Search for "HAOS Agent Magdala" and install it
8. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [releases page](https://github.com/GitDakky/HAOS_Agent_Magdala/releases)
2. Extract the `custom_components/agent_magdala` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "HAOS Agent Magdala"
4. Enter your configuration:
   - **OpenRouter API Key**: Your OpenRouter API key for AI model access
   - **Mem0 API Key**: Your Mem0 API key for persistent memory
   - **OpenRouter Model**: AI model to use (default: `google/gemini-flash-1.5`)
   - **Guardian Mode**: Enable proactive monitoring and alerts
   - **Voice Announcements**: Enable TTS communication via speakers

## Guardian in Action

### 🌅 Morning Briefing
*"Good morning, David. I've noticed you're up 30 minutes early today. I've started the coffee maker and adjusted the thermostat to 72°F. Your first meeting is at 9 AM, and traffic is light on your usual route."*

### 🚨 Security Alert
*"David, I've detected motion in the backyard at 2:15 AM. The security camera shows a raccoon near the garbage cans. I've logged this event and increased exterior lighting for the next hour."*

### 💊 Wellness Check
*"It's 8 PM and time for your evening medication. I've also noticed the air quality has dropped due to wildfire smoke. I've activated the air purifier in the bedroom."*

### ⚡ Energy Optimization
*"I've noticed the washing machine has been running during peak energy hours. I can schedule it to run at 11 PM when rates are 40% lower. Would you like me to set this up automatically?"*

## 💬 Chat Interface

### Custom Lovelace Card
The integration includes a beautiful chat interface card for your dashboard:

```yaml
type: custom:agent-magdala-chat-card
title: "🤖 Agent Magdala Guardian"
theme: dark  # or light
height: 500px
```

**Features:**
- **Real-time chat** with your AI Guardian
- **Conversation history** maintained across sessions
- **Typing indicators** and status updates
- **Cyberpunk aesthetic** with green/black theme
- **Mobile responsive** design

### Dashboard Integration
The integration creates several entities for full dashboard control:

**Sensors:**
- `sensor.agent_magdala_status` - Agent health status
- `sensor.agent_magdala_mode` - Current guardian mode
- `sensor.agent_magdala_conversations` - Active conversation count
- `sensor.agent_magdala_last_interaction` - Last activity timestamp

**Switches:**
- `switch.agent_magdala_guardian_active` - Toggle guardian mode
- `switch.agent_magdala_security_module` - Security monitoring
- `switch.agent_magdala_wellness_module` - Wellness monitoring
- `switch.agent_magdala_energy_module` - Energy monitoring

**Binary Sensors:**
- `binary_sensor.agent_magdala_agent_online` - Agent availability
- `binary_sensor.agent_magdala_api_connected` - API connection status

## Services & Events

### Service: `agent_magdala.ask`
Send a prompt to the guardian agent:
```yaml
service: agent_magdala.ask
data:
  prompt: "What's the security status of the house?"
  conversation_id: "optional-conversation-id"
```

### Service: `agent_magdala.guardian_mode`
Control guardian monitoring:
```yaml
service: agent_magdala.guardian_mode
data:
  mode: "active"  # active, passive, sleep
  modules: ["security", "wellness", "energy"]
```

### Service: `agent_magdala.control_device`
Control devices through the agent:
```yaml
service: agent_magdala.control_device
data:
  entity_id: "light.living_room"
  action: "turn_on"
  brightness: 200
```

### Events
- `agent_magdala_response`: Agent responses and confirmations
- `agent_magdala_alert`: Security and safety alerts
- `agent_magdala_pattern`: Learned pattern notifications

## Development Roadmap

### Phase 1: Foundation ✅
- [x] Replace LangChain with Pydantic AI SDK
- [x] Integrate Mem0 memory system
- [x] Set up basic sensor monitoring
- [x] Implement TTS communication

### Phase 2: Guardian Behaviors 🚧
- [ ] Security monitoring and alerts
- [ ] Basic pattern learning
- [ ] Proactive voice announcements
- [ ] Energy usage tracking

### Phase 3: Intelligence 📋
- [ ] Advanced pattern recognition
- [ ] Multi-user preferences
- [ ] Predictive behaviors
- [ ] Wellness monitoring

### Phase 4: Refinement 📋
- [ ] User feedback integration
- [ ] Performance optimization
- [ ] Advanced scenarios
- [ ] Documentation and testing

## Privacy & Security

- **🔒 Local Processing**: All AI processing happens on your Home Assistant instance
- **🚫 No Cloud Dependencies**: Optional cloud APIs only for enhanced AI models
- **🛡️ Encrypted Storage**: All memory and preferences stored securely
- **👥 Family Privacy**: Individual user profiles with separate data isolation
- **🔍 Audit Trail**: Complete logging of all guardian actions and decisions

## Troubleshooting

### Guardian Not Responding
1. Check that OpenRouter and Mem0 API keys are valid
2. Verify TTS service is configured in Home Assistant
3. Ensure guardian mode is enabled in integration settings
4. Check Home Assistant logs for error messages

### Memory Not Persisting
1. Verify Mem0 API key and connectivity
2. Check storage permissions in Home Assistant
3. Review memory configuration in integration settings

## Contributing

We welcome contributions to make HAOS Agent Magdala even better! Please:

1. **Fork the repository** and create a feature branch
2. **Follow the coding standards** (type hints, Pydantic models, async patterns)
3. **Add tests** for new guardian behaviors
4. **Update documentation** for new features
5. **Submit a pull request** with detailed description

### Development Setup
```bash
# Clone the repository
git clone https://github.com/GitDakky/HAOS_Agent_Magdala.git

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run type checking
mypy custom_components/agent_magdala/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 🐛 [Report Issues](https://github.com/GitDakky/HAOS_Agent_Magdala/issues)
- 💬 [Discussions](https://github.com/GitDakky/HAOS_Agent_Magdala/discussions)
- 📖 [Documentation](https://github.com/GitDakky/HAOS_Agent_Magdala/wiki)
- 🎥 [Video Tutorials](https://github.com/GitDakky/HAOS_Agent_Magdala/wiki/tutorials)

## Acknowledgments

- 🧠 Built with [Pydantic AI SDK](https://github.com/pydantic/pydantic-ai) for type-safe AI agents
- 💾 Powered by [Mem0](https://mem0.ai/) for intelligent memory management
- 🗣️ Integrated with [Home Assistant TTS](https://www.home-assistant.io/integrations/tts/) for voice communication
- 🏠 Inspired by the amazing [Home Assistant](https://www.home-assistant.io/) community

---

**Transform your Home Assistant into an intelligent guardian that truly understands and protects your home. Welcome to the future of smart home automation! 🏠🤖**