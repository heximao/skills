---
name: opencode-custom-model-config
description: Expert guide for configuring OpenCode (opencode-ai) with custom LLMs via gateways like New API.
---

# OpenCode Custom Model Configuration

Expert guide for configuring OpenCode (opencode-ai) with custom LLMs via gateways like New API/One API.

## Core Configuration Structure

Edit `opencode.jsonc` or `config.json` to define custom providers and models.

```jsonc
"provider": {
  "my-custom-provider": {
    "name": "CustomProvider",
    "npm": "@ai-sdk/openai-compatible", // or @ai-sdk/anthropic, @ai-sdk/google
    "options": {
      "baseURL": "http://<gateway-ip>:3000/v1",
      "apiKey": "your-token",
      "setCacheKey": true // Recommended for prompt caching
    },
    "models": {
      "openai/o1-glm-4-5": { // Prefix with o1 to trick UI into showing reasoning slider
        "name": "GLM-4.5",
        "thinking": true,
        "limit": {
          "context": 131072,
          "output": 32768
        },
        "variant": {
          "high": {
            "name": "High Reasoning",
            "limit": { "context": 131072, "output": 49152 } // Reserved for thinking + response
          }
        }
      }
    }
  }
}
```

## Token Calculation Logic

For models where thinking tokens and response tokens share the same output window (e.g., GLM-4.5, DeepSeek):

1. **Input Space** = `limit.context` - `limit.output`.
2. **Safety Margin**: Set `limit.output` to `max_thinking_tokens + expected_response_tokens`.
   - *Example (GLM-4.5)*: 32,768 (thinking) + 16,384 (response) = 49,152 output.
   - *Result*: 131,072 (total) - 49,152 (output) = 81,920 (safe input).

## UI Triggers

- **Reasoning Slider**: Only appears if Model ID starts with `o1` or `o3`.
- **Variant Keys**: Must be exactly `minimal`, `low`, `medium`, `high`, or `max`.
- **Thinking Blocks**: Set `"thinking": true` to enable dedicated UI area for reasoning content.

## Native Protocol Relay

If the gateway (like New API) supports native relay:
- Use `@ai-sdk/anthropic` for Claude models to get better caching and thinking block support.
- Use `@ai-sdk/google` for Gemini to handle massive context windows (1M+).
