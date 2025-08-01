# LLM Configuration Guide

This document explains how to configure and use different Language Model providers in the AI Event Planner system.

## Supported LLM Providers

The system currently supports the following LLM providers:

1. **OpenAI** (default) - Uses models like GPT-4, GPT-3.5-turbo
2. **Google AI** - Uses models like Gemini Pro

## Configuration

LLM configuration is managed through environment variables in the `.env` file:

```
# LLM Provider (options: "openai" or "google")
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key
GOOGLE_MODEL=gemini-pro
```

### Required Environment Variables

- `LLM_PROVIDER`: Specifies which LLM provider to use. Options are "openai" or "google".
- `OPENAI_API_KEY`: Your OpenAI API key (required if using OpenAI).
- `LLM_MODEL`: The OpenAI model to use (e.g., "gpt-4", "gpt-3.5-turbo").
- `GOOGLE_API_KEY`: Your Google AI API key (required if using Google AI).
- `GOOGLE_MODEL`: The Google AI model to use (e.g., "gemini-pro").

## How to Switch Between Providers

To switch between LLM providers, simply update the `LLM_PROVIDER` value in your `.env` file:

```
# To use OpenAI
LLM_PROVIDER=openai

# To use Google AI
LLM_PROVIDER=google
```

Make sure you have the appropriate API key set for the provider you're using.

## Getting API Keys

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to API keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### Google AI API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

## Testing LLM Providers

You can test both LLM providers using the provided test script:

```bash
python test_llm_providers.py
```

This script will test both OpenAI and Google AI (if configured) and display the results.

## Implementation Details

The system uses a factory pattern to create the appropriate LLM instance based on the configuration:

- `app/utils/llm_factory.py` contains the `get_llm()` function that returns the configured LLM
- All agent graphs use this factory function to get the LLM instance

## Dependency Management

The project uses Poetry for dependency management. The Google AI dependencies are now optional to avoid dependency conflicts during deployment:

```toml
[tool.poetry.dependencies]
# Main dependencies
python = "^3.10"
langgraph = "^0.1.11"
langchain = "^0.1.0"
langchain-openai = "^0.0.5"
# ... other dependencies

[tool.poetry.group.google.dependencies]
langchain-google-genai = "^0.0.5"
```

### Installing Dependencies

- **For development with OpenAI only**:
  ```bash
  poetry install --without google
  ```

- **For development with both OpenAI and Google AI**:
  ```bash
  poetry install
  ```

- **For production deployment** (Azure):
  The deployment automatically excludes Google AI dependencies to avoid conflicts.

## Troubleshooting

### Common Issues

1. **"API key not set" error**:
   - Make sure you've set the appropriate API key in your `.env` file
   - Check that the key is valid and has not expired

2. **"Provider not supported" error**:
   - Check that `LLM_PROVIDER` is set to either "openai" or "google"

3. **"Module not found" error for Google AI**:
   - If you're trying to use Google AI, make sure you've installed the Google dependencies:
     ```bash
     poetry install --with google
     ```

4. **Rate limiting or quota issues**:
   - Check your API usage on the provider's dashboard
   - Consider upgrading your API plan if you're hitting limits

5. **Dependency conflicts during deployment**:
   - The deployment is configured to use only OpenAI dependencies
   - If you need to use Google AI in production, you'll need to modify the Dockerfile and GitHub workflow
