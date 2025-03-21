# MCP Servers for AI-EventPlanner

This directory contains Model Context Protocol (MCP) servers that extend the AI-EventPlanner application with additional capabilities:

1. **SendGrid MCP Server**: Provides email functionality
2. **OpenWeather MCP Server**: Provides weather data and forecasting

## Architecture

These MCP servers are designed to work in both local development and Azure deployment environments:

- **Local Development**: The servers are run as separate processes and communicate with the main application via stdio
- **Azure Deployment**: The servers are embedded in the main application container and communicate via localhost TCP

## SendGrid MCP Server

The SendGrid MCP server provides email functionality through the SendGrid API.

### Tools

- `send_email`: Send an email to a single recipient
- `send_bulk_emails`: Send emails to multiple recipients
- `create_email_template`: Create a new email template
- `list_email_templates`: List all available email templates
- `get_email_template`: Get a specific email template by ID

### Configuration

The SendGrid MCP server requires a SendGrid API key, which should be provided in the environment variable `SENDGRID_API_KEY`.

## OpenWeather MCP Server

The OpenWeather MCP server provides weather data and forecasting through the OpenWeather API.

### Tools

- `get_forecast`: Get weather forecast for a city
- `check_weather_risks`: Check weather-related risks for an event

### Resources

The OpenWeather MCP server also provides resources for accessing current weather data:

- `weather://{city}/current`: Current weather data for a city

### Configuration

The OpenWeather MCP server requires an OpenWeather API key, which should be provided in the environment variable `OPENWEATHER_API_KEY`.

## Integration with AI-EventPlanner

The MCP servers are integrated with the AI-EventPlanner application through the MCP adapter in `app/utils/mcp_adapter.py`. This adapter provides:

- A common interface for communicating with MCP servers
- Support for both local development and Azure deployment
- Convenience functions for common operations

### Example Usage

```python
from app.utils.mcp_adapter import send_email, get_weather_forecast

# Send an email
send_email(
    to_email="recipient@example.com",
    to_name="John Doe",
    subject="Hello from AI-EventPlanner",
    content="<h1>Hello!</h1><p>This is a test email.</p>"
)

# Get a weather forecast
forecast = get_weather_forecast(city="New York", days=3)
print(f"Weather forecast for {forecast['location']}:")
for day in forecast['daily']:
    print(f"Date: {day['date']}")
    print(f"  Temperature: {day['temperature']['min']}°C to {day['temperature']['max']}°C")
    print(f"  Conditions: {day['conditions']}")
```

See `examples/mcp_example.py` for more examples.

## Deployment

The MCP servers are automatically deployed with the main application when using the provided Dockerfile. The Dockerfile:

1. Installs Node.js for running the MCP servers
2. Copies the MCP server code to the container
3. Installs the MCP server dependencies
4. Starts the MCP servers alongside the main application

## Azure Configuration

When deploying to Azure, you should configure the following App Settings:

- `SENDGRID_API_KEY`: Your SendGrid API key
- `OPENWEATHER_API_KEY`: Your OpenWeather API key

For enhanced security, it's recommended to store these keys in Azure Key Vault and configure the App Service to access them using managed identity.
