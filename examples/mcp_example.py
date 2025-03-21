"""
Example script demonstrating how to use the MCP adapter to interact with MCP servers.

This script shows how to:
1. Send an email using the SendGrid MCP server
2. Get a weather forecast using the OpenWeather MCP server
3. Check weather risks for an event using the OpenWeather MCP server
4. Get current weather data using the OpenWeather MCP server
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.mcp_adapter import (
    send_email,
    send_bulk_emails,
    get_weather_forecast,
    check_weather_risks,
    get_current_weather
)

def print_section(title):
    """Print a section title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_json(data):
    """Print JSON data in a readable format."""
    print(json.dumps(data, indent=2))

def example_send_email():
    """Example of sending an email."""
    print_section("Sending an Email")
    
    # Send an email
    result = send_email(
        to_email="recipient@example.com",
        to_name="John Doe",
        subject="Hello from AI-EventPlanner",
        content="<h1>Hello!</h1><p>This is a test email sent from the AI-EventPlanner application.</p>",
        from_email="sender@example.com",
        from_name="AI-EventPlanner"
    )
    
    print("Email sent!")
    print_json(result)

def example_send_bulk_emails():
    """Example of sending bulk emails."""
    print_section("Sending Bulk Emails")
    
    # Define recipients
    recipients = [
        {"email": "recipient1@example.com", "name": "John Doe"},
        {"email": "recipient2@example.com", "name": "Jane Smith"},
        {"email": "recipient3@example.com", "name": "Bob Johnson"}
    ]
    
    # Send bulk emails
    result = send_bulk_emails(
        to_list=recipients,
        subject="Event Invitation",
        content="<h1>You're Invited!</h1><p>Join us for our upcoming event.</p>",
        from_email="events@example.com",
        from_name="Event Team",
        is_personalized=True
    )
    
    print("Bulk emails sent!")
    print_json(result)

def example_get_weather_forecast():
    """Example of getting a weather forecast."""
    print_section("Getting Weather Forecast")
    
    # Get a weather forecast for New York for the next 3 days
    forecast = get_weather_forecast(city="New York", days=3)
    
    print(f"Weather forecast for {forecast['location']}:")
    for day in forecast['daily']:
        print(f"Date: {day['date']}")
        print(f"  Temperature: {day['temperature']['min']}°C to {day['temperature']['max']}°C")
        print(f"  Conditions: {day['conditions']}")
        print(f"  Precipitation Probability: {day['precipitation_probability']}%")
        print(f"  Wind Speed: {day['wind_speed']} m/s")
        print()

def example_check_weather_risks():
    """Example of checking weather risks for an event."""
    print_section("Checking Weather Risks for an Event")
    
    # Calculate a date 2 days from now
    event_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # Check weather risks for an outdoor event
    risks = check_weather_risks(
        location="Chicago",
        event_date=event_date,
        event_type="outdoor concert",
        attendee_count=1000
    )
    
    print(f"Weather risk assessment:")
    print(f"Risk Level: {risks['risk_level']}")
    print(f"Description: {risks['description']}")
    print("Recommendations:")
    for recommendation in risks['recommendations']:
        print(f"  - {recommendation}")

def example_get_current_weather():
    """Example of getting current weather data."""
    print_section("Getting Current Weather")
    
    # Get current weather for London
    weather = get_current_weather(city="London")
    
    print(f"Current weather in {weather['location']}:")
    print(f"Temperature: {weather['temperature']}°C")
    print(f"Conditions: {weather['conditions']}")
    print(f"Humidity: {weather['humidity']}%")
    print(f"Wind Speed: {weather['wind_speed']} m/s")
    print(f"Timestamp: {weather['timestamp']}")

def main():
    """Run all examples."""
    print_section("MCP Adapter Examples")
    
    try:
        # Run the email examples
        example_send_email()
        example_send_bulk_emails()
        
        # Run the weather examples
        example_get_weather_forecast()
        example_check_weather_risks()
        example_get_current_weather()
        
        print_section("All Examples Completed Successfully")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
