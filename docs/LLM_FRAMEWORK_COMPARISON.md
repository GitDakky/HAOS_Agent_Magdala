# LLM Framework Comparison for Home Assistant Integration

## Executive Summary

This document analyzes alternative AI/LLM frameworks to replace LangChain in the HAOS Agent Magdala integration. The analysis focuses on lightweight frameworks with minimal dependencies, async support, tool calling capabilities, and compatibility with OpenRouter and Home Assistant requirements.

## Current Implementation Analysis

The current implementation uses:
- **LangChain** with `langchain_openai` and `langchain_perplexity`
- **Tool calling** via `@tool` decorator and `create_tool_calling_agent`
- **Async handling** via `hass.async_add_executor_job` (blocking calls in executor)
- **OpenRouter** support via OpenAI-compatible endpoint

## Framework Comparison

### 1. LiteLLM
**GitHub**: https://github.com/BerriAI/litellm

#### Pros:
- ✅ **Excellent async support** - Native async/await for all operations
- ✅ **OpenRouter compatible** - Works with OpenAI-style APIs
- ✅ **Minimal dependencies** - Only requires `openai>=1.0.0` and `pydantic>=2.0.0`
- ✅ **Active maintenance** - Regular updates and large community
- ✅ **Built-in rate limiting and retry logic**
- ✅ **Supports 30+ providers** including OpenRouter

#### Cons:
- ❌ **No built-in agent framework** - Would need custom implementation
- ❌ **Limited tool calling** - Requires manual function calling implementation

#### Implementation Example:
```python
import litellm
from litellm import acompletion

# Async completion with OpenRouter
response = await acompletion(
    model="openrouter/anthropic/claude-3-opus",
    messages=[{"role": "user", "content": "Hello"}],
    api_base="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key
)
```

### 2. Instructor
**GitHub**: https://github.com/jxnl/instructor

#### Pros:
- ✅ **Type-safe structured outputs** - Excellent Pydantic integration
- ✅ **Async support** - Native async/await capabilities
- ✅ **Minimal dependencies** - Built on top of standard OpenAI SDK
- ✅ **OpenRouter compatible** - Works with any OpenAI-compatible API
- ✅ **Active maintenance** - Well-maintained with good documentation

#### Cons:
- ❌ **No agent framework** - Focused on structured extraction
- ❌ **Limited tool calling** - Not designed for multi-tool agents

#### Implementation Example:
```python
import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel

client = instructor.from_openai(
    AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key
    )
)

class ServiceCall(BaseModel):
    domain: str
    service: str
    entity_id: str

response = await client.chat.completions.create(
    model="anthropic/claude-3-opus",
    response_model=ServiceCall,
    messages=[{"role": "user", "content": "Turn on the living room lights"}]
)
```

### 3. Marvin
**GitHub**: https://github.com/prefecthq/marvin

#### Pros:
- ✅ **Task-oriented design** - Good for automation workflows
- ✅ **Tool support** - Native tool/function integration
- ✅ **Structured outputs** - Good Pydantic support
- ✅ **Thread management** - Built-in conversation history

#### Cons:
- ❌ **Heavier dependencies** - Requires Pydantic AI and SQLite
- ❌ **Unclear async support** - Documentation doesn't emphasize async
- ❌ **Less flexible** - More opinionated framework

### 4. Guidance
**GitHub**: https://github.com/guidance-ai/guidance

#### Pros:
- ✅ **Excellent constrained generation** - Perfect for structured commands
- ✅ **Multi-backend support** - Works with various models
- ✅ **Token-efficient** - Reduces API calls through stateful control
- ✅ **Tool calling support** - Automatic interruption/resumption

#### Cons:
- ❌ **Learning curve** - Unique templating syntax
- ❌ **Unclear async support** - Not emphasized in docs
- ❌ **Less suitable for conversational agents**

### 5. Outlines
**GitHub**: https://github.com/outlines-dev/outlines

#### Pros:
- ✅ **Strong structured generation** - JSON, regex, grammar constraints
- ✅ **Lightweight** - Minimal dependencies
- ✅ **Type constraints** - Good for command parsing

#### Cons:
- ❌ **No async support mentioned**
- ❌ **Limited tool calling** - Focused on generation constraints
- ❌ **Not designed for agents** - More for structured output

### 6. Direct OpenAI SDK Approach

#### Pros:
- ✅ **Minimal dependencies** - Just `openai` package
- ✅ **Native async support** - AsyncOpenAI client
- ✅ **Function calling** - Built-in support
- ✅ **OpenRouter compatible** - Works perfectly
- ✅ **Full control** - No framework overhead

#### Cons:
- ❌ **More code to write** - Need custom agent logic
- ❌ **No built-in conversation management**

#### Implementation Example:
```python
from openai import AsyncOpenAI
import json

class DirectAgent:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    
    async def call_with_tools(self, messages, tools):
        response = await self.client.chat.completions.create(
            model="anthropic/claude-3-opus",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        # Handle tool calls
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                # Execute tool and get result
                result = await self.execute_tool(
                    tool_call.function.name,
                    json.loads(tool_call.function.arguments)
                )
```

## Recommendation for Home Assistant Integration

Based on the analysis, here are my recommendations in order of preference:

### 1. **LiteLLM + Custom Agent Logic** (Recommended)
- **Why**: Excellent async support, minimal dependencies, OpenRouter compatible
- **Implementation**: Use LiteLLM for LLM calls, implement custom tool calling logic
- **Dependencies**: `litellm`, `openai>=1.0.0`, `pydantic>=2.0.0`

### 2. **Direct OpenAI SDK**
- **Why**: Maximum control, native async, minimal dependencies
- **Implementation**: Use AsyncOpenAI with custom agent logic
- **Dependencies**: Just `openai`

### 3. **Instructor + Custom Agent**
- **Why**: Great for structured outputs, async support
- **Implementation**: Use for parsing user intents into service calls
- **Dependencies**: `instructor`, `openai`, `pydantic`

## Migration Strategy

Here's a proposed migration path from LangChain to LiteLLM:

```python
# New agent.py structure
import litellm
from litellm import acompletion
import json
from typing import List, Dict, Any

class MagdalaAgent:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.tools = self._initialize_tools()
        
    async def get_response(self, prompt: str) -> str:
        # System prompt with tool descriptions
        system_prompt = self._build_system_prompt()
        
        # Call LLM with tools
        response = await acompletion(
            model=f"openrouter/{self.entry.data.get('model')}",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            api_base="https://openrouter.ai/api/v1",
            api_key=self.entry.data.get(CONF_OPENROUTER_API_KEY),
            functions=self._get_tool_definitions()
        )
        
        # Handle function calls
        if response.choices[0].message.get("function_call"):
            result = await self._execute_function(
                response.choices[0].message["function_call"]
            )
            # Continue conversation with result
            
        return response.choices[0].message.content
```

## Dependency Comparison

| Framework | Core Dependencies | Total Size (approx) |
|-----------|------------------|-------------------|
| LangChain | 20+ packages | ~50MB |
| LiteLLM | 2-3 packages | ~5MB |
| Direct OpenAI | 1 package | ~2MB |
| Instructor | 2-3 packages | ~3MB |
| Marvin | 5+ packages | ~15MB |

## Conclusion

For the Home Assistant integration, **LiteLLM** offers the best balance of:
- Minimal dependencies
- Excellent async support
- OpenRouter compatibility
- Active maintenance
- Flexibility for custom agent implementation

The migration would significantly reduce the dependency footprint while maintaining all required functionality and improving async performance.