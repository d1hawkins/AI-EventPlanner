#!/usr/bin/env python3
"""
Direct test script for MCP servers using the MCP adapter.

This script tests the SendGrid and OpenWeather MCP servers by:
1. Using the MCP adapter to communicate with the servers
2. Calling the tools and accessing the resources
3. Verifying the responses

Usage:
    python test_mcp_direct.py

Environment variables:
    SENDGRID_API_KEY: SendGrid API key
    OPENWEATHER_API_KEY: OpenWeather API key
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import the MCP adapter
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

def test_sendgrid():
    """Test the SendGrid MCP server."""
    print_section("Testing SendGrid MCP Server")
    
    # Check if SendGrid API key is set
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    if not sendgrid_api_key:
        print("Warning: SENDGRID_API_KEY environment variable is not set.")
        print("SendGrid tests will be skipped.")
        return False
    
    try:
        # Test 1: Send an email
        print("Test 1: Send an email")
        result = send_email(
            to_email="recipient@example.com",
            to_name="John Doe",
            subject="Test Email from AI-EventPlanner",
            content="<h1>Hello!</h1><p>This is a test email sent from the AI-EventPlanner application.</p>",
            from_email="sender@example.com",
            from_name="AI-EventPlanner"
        )
        
        print("Email sent successfully!")
        print_json(result)
        
        # Test 2: Send bulk emails
        print("\nTest 2: Send bulk emails")
        recipients = [
            {"email": "recipient1@example.com", "name": "John Doe"},
            {"email": "recipient2@example.com", "name": "Jane Smith"},
            {"email": "recipient3@example.com", "name": "Bob Johnson"}
        ]
        
        result = send_bulk_emails(
            to_list=recipients,
            subject="Test Bulk Email from AI-EventPlanner",
            content="<h1>Hello!</h1><p>This is a test bulk email sent from the AI-EventPlanner application.</p>",
            from_email="sender@example.com",
            from_name="AI-EventPlanner",
            is_personalized=True
        )
        
        print("Bulk emails sent successfully!")
        print_json(result)
        
        print("\nSendGrid MCP server tests completed successfully")
        return True
    
    except Exception as e:
        print(f"Error testing SendGrid MCP server: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_openweather():
    """Test the OpenWeather MCP server."""
    print_section("Testing OpenWeather MCP Server")
    
    # Check if OpenWeather API key is set
    openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
    if not openweather_api_key:
        print("Warning: OPENWEATHER_API_KEY environment variable is not set.")
        print("OpenWeather tests will be skipped.")
        return False
    
    try:
        # Test 1: Get weather forecast
        print("Test 1: Get weather forecast")
        forecast = get_weather_forecast(city="New York", days=3)
        
        print(f"Weather forecast for {forecast['location']}:")
        for day in forecast['daily']:
            print(f"Date: {day['date']}")
            print(f"  Temperature: {day['temperature']['min']}°C to {day['temperature']['max']}°C")
            print(f"  Conditions: {day['conditions']}")
            print(f"  Precipitation Probability: {day['precipitation_probability']}%")
            print(f"  Wind Speed: {day['wind_speed']} m/s")
            print()
        
        # Test 2: Check weather risks
        print("\nTest 2: Check weather risks")
        event_date = datetime.now().strftime("%Y-%m-%d")
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
        
        # Test 3: Get current weather
        print("\nTest 3: Get current weather")
        weather = get_current_weather(city="London")
        
        print(f"Current weather in {weather['location']}:")
        print(f"Temperature: {weather['temperature']}°C")
        print(f"Conditions: {weather['conditions']}")
        print(f"Humidity: {weather['humidity']}%")
        print(f"Wind Speed: {weather['wind_speed']} m/s")
        print(f"Timestamp: {weather['timestamp']}")
        
        print("\nOpenWeather MCP server tests completed successfully")
        return True
    
    except Exception as e:
        print(f"Error testing OpenWeather MCP server: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print_section("MCP Server Direct Tests")
    
    # Test SendGrid MCP server
    sendgrid_success = test_sendgrid()
    
    # Test OpenWeather MCP server
    openweather_success = test_openweather()
    
    # Print summary
    print_section("Test Summary")
    print(f"SendGrid MCP server: {'PASS' if sendgrid_success else 'FAIL'}")
    print(f"OpenWeather MCP server: {'PASS' if openweather_success else 'FAIL'}")
    
    # Return exit code
    if sendgrid_success and openweather_success:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
