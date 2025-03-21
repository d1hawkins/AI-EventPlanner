#!/usr/bin/env node

/**
 * OpenWeather MCP Server
 * This server provides weather data functionality using the OpenWeather API.
 * It allows:
 * - Getting weather forecasts for locations
 * - Checking weather-related risks for events
 * - Accessing current weather data as resources
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

/**
 * Type definitions for weather data
 */
type WeatherData = {
  location: string;
  temperature: number;
  conditions: string;
  humidity: number;
  wind_speed: number;
  timestamp: string;
};

type ForecastData = {
  location: string;
  daily: Array<{
    date: string;
    temperature: {
      min: number;
      max: number;
    };
    conditions: string;
    precipitation_probability: number;
    wind_speed: number;
  }>;
};

type WeatherRisk = {
  risk_level: "low" | "medium" | "high";
  description: string;
  recommendations: string[];
};

/**
 * Cache for weather data to avoid repeated API calls
 */
const weatherCache: { [location: string]: { data: WeatherData, timestamp: number } } = {};
const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes in milliseconds

/**
 * Initialize the OpenWeather API client with the API key from environment variables.
 * The API key should be provided in the MCP settings configuration.
 */
const getApiKey = () => {
  const apiKey = process.env.OPENWEATHER_API_KEY;
  if (!apiKey) {
    console.error("OPENWEATHER_API_KEY environment variable is required");
    return null;
  }
  return apiKey;
};

/**
 * Create an MCP server with capabilities for weather tools and resources.
 */
const server = new Server(
  {
    name: "openweather-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      resources: {},
      tools: {},
    },
  }
);

/**
 * Handler for listing available weather resources.
 * Exposes current weather for popular cities as resources.
 */
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  const popularCities = [
    "New York",
    "London",
    "Tokyo",
    "Paris",
    "Sydney",
    "San Francisco"
  ];

  return {
    resources: popularCities.map(city => ({
      uri: `weather://${encodeURIComponent(city)}/current`,
      mimeType: "application/json",
      name: `Current weather in ${city}`,
      description: `Real-time weather data for ${city} including temperature, conditions, humidity, and wind speed`
    }))
  };
});

/**
 * Handler for reading weather resources.
 * Takes a weather:// URI and returns the current weather data.
 */
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new McpError(
      ErrorCode.InternalError,
      "OpenWeather API key not configured"
    );
  }

  const match = request.params.uri.match(/^weather:\/\/([^/]+)\/current$/);
  if (!match) {
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Invalid URI format: ${request.params.uri}`
    );
  }

  const location = decodeURIComponent(match[1]);
  
  // Check cache first
  const now = Date.now();
  if (weatherCache[location] && (now - weatherCache[location].timestamp) < CACHE_DURATION) {
    return {
      contents: [{
        uri: request.params.uri,
        mimeType: "application/json",
        text: JSON.stringify(weatherCache[location].data, null, 2)
      }]
    };
  }

  try {
    const response = await axios.get("https://api.openweathermap.org/data/2.5/weather", {
      params: {
        q: location,
        appid: apiKey,
        units: "metric"
      }
    });

    const data = response.data;
    const weatherData: WeatherData = {
      location: data.name,
      temperature: data.main.temp,
      conditions: data.weather[0].description,
      humidity: data.main.humidity,
      wind_speed: data.wind.speed,
      timestamp: new Date().toISOString()
    };

    // Update cache
    weatherCache[location] = {
      data: weatherData,
      timestamp: now
    };

    return {
      contents: [{
        uri: request.params.uri,
        mimeType: "application/json",
        text: JSON.stringify(weatherData, null, 2)
      }]
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new McpError(
        ErrorCode.InternalError,
        `Weather API error: ${error.response?.data.message || error.message}`
      );
    }
    throw error;
  }
});

/**
 * Handler that lists available weather tools.
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_forecast",
        description: "Get weather forecast for a city",
        inputSchema: {
          type: "object",
          properties: {
            city: {
              type: "string",
              description: "City name"
            },
            days: {
              type: "number",
              description: "Number of days (1-5)",
              minimum: 1,
              maximum: 5
            }
          },
          required: ["city"]
        }
      },
      {
        name: "check_weather_risks",
        description: "Check weather-related risks for an event",
        inputSchema: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "Event location (city name)"
            },
            event_date: {
              type: "string",
              description: "Event date (YYYY-MM-DD)"
            },
            event_type: {
              type: "string",
              description: "Type of event (e.g., outdoor, indoor, sports)"
            },
            attendee_count: {
              type: "number",
              description: "Expected number of attendees"
            }
          },
          required: ["location", "event_date", "event_type"]
        }
      }
    ]
  };
});

/**
 * Handler for weather tools.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new McpError(
      ErrorCode.InternalError,
      "OpenWeather API key not configured"
    );
  }

  switch (request.params.name) {
    case "get_forecast": {
      const { city, days = 3 } = request.params.arguments as any;
      
      if (!city) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "City name is required"
        );
      }

      const daysCount = Math.min(Math.max(1, days), 5); // Ensure days is between 1 and 5

      try {
        // First, get coordinates for the city
        const geoResponse = await axios.get("http://api.openweathermap.org/geo/1.0/direct", {
          params: {
            q: city,
            limit: 1,
            appid: apiKey
          }
        });

        if (!geoResponse.data || geoResponse.data.length === 0) {
          throw new McpError(
            ErrorCode.InvalidParams,
            `City not found: ${city}`
          );
        }

        const { lat, lon } = geoResponse.data[0];

        // Then, get the forecast using the coordinates
        const forecastResponse = await axios.get("https://api.openweathermap.org/data/2.5/forecast", {
          params: {
            lat,
            lon,
            appid: apiKey,
            units: "metric",
            cnt: daysCount * 8 // 8 data points per day (every 3 hours)
          }
        });

        const data = forecastResponse.data;
        
        // Process the forecast data to get daily summaries
        const dailyForecasts = [];
        const forecastsByDay: Record<string, any[]> = {};

        // Group forecasts by day
        for (const item of data.list) {
          const date = new Date(item.dt * 1000).toISOString().split('T')[0];
          if (!forecastsByDay[date]) {
            forecastsByDay[date] = [];
          }
          forecastsByDay[date].push(item);
        }

        // Create daily summaries
        for (const [date, forecasts] of Object.entries(forecastsByDay)) {
          if (dailyForecasts.length >= daysCount) break;

          const temperatures = forecasts.map(f => f.main.temp);
          const minTemp = Math.min(...temperatures);
          const maxTemp = Math.max(...temperatures);
          
          // Get the most common weather condition
          const conditionCounts: Record<string, number> = {};
          for (const forecast of forecasts) {
            const condition = forecast.weather[0].description;
            conditionCounts[condition] = (conditionCounts[condition] || 0) + 1;
          }
          const mainCondition = Object.entries(conditionCounts)
            .sort((a, b) => b[1] - a[1])[0][0];
          
          // Calculate average wind speed and precipitation probability
          const avgWindSpeed = forecasts.reduce((sum, f) => sum + f.wind.speed, 0) / forecasts.length;
          const precipProbability = forecasts.some(f => f.pop > 0) 
            ? Math.max(...forecasts.map(f => f.pop || 0)) * 100 
            : 0;

          dailyForecasts.push({
            date,
            temperature: {
              min: Math.round(minTemp * 10) / 10,
              max: Math.round(maxTemp * 10) / 10
            },
            conditions: mainCondition,
            precipitation_probability: Math.round(precipProbability),
            wind_speed: Math.round(avgWindSpeed * 10) / 10
          });
        }

        const forecastData: ForecastData = {
          location: `${data.city.name}, ${data.city.country}`,
          daily: dailyForecasts
        };

        return {
          content: [{
            type: "text",
            text: JSON.stringify(forecastData, null, 2)
          }]
        };
      } catch (error) {
        if (axios.isAxiosError(error)) {
          throw new McpError(
            ErrorCode.InternalError,
            `Weather API error: ${error.response?.data.message || error.message}`
          );
        }
        throw error;
      }
    }

    case "check_weather_risks": {
      const { location, event_date, event_type, attendee_count = 100 } = request.params.arguments as any;
      
      if (!location || !event_date || !event_type) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "Location, event date, and event type are required"
        );
      }

      try {
        // Parse the event date
        const eventDateObj = new Date(event_date);
        const today = new Date();
        
        // Calculate days until event
        const daysUntilEvent = Math.ceil((eventDateObj.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
        
        if (daysUntilEvent < 0) {
          throw new McpError(
            ErrorCode.InvalidParams,
            "Event date must be in the future"
          );
        }

        // If event is within forecast range (5 days), get actual forecast
        if (daysUntilEvent <= 5) {
          // First, get coordinates for the location
          const geoResponse = await axios.get("http://api.openweathermap.org/geo/1.0/direct", {
            params: {
              q: location,
              limit: 1,
              appid: apiKey
            }
          });

          if (!geoResponse.data || geoResponse.data.length === 0) {
            throw new McpError(
              ErrorCode.InvalidParams,
              `Location not found: ${location}`
            );
          }

          const { lat, lon } = geoResponse.data[0];

          // Then, get the forecast using the coordinates
          const forecastResponse = await axios.get("https://api.openweathermap.org/data/2.5/forecast", {
            params: {
              lat,
              lon,
              appid: apiKey,
              units: "metric"
            }
          });

          const data = forecastResponse.data;
          
          // Find forecasts for the event date
          const eventDateStr = eventDateObj.toISOString().split('T')[0];
          const eventForecasts = data.list.filter((item: any) => {
            const forecastDate = new Date(item.dt * 1000).toISOString().split('T')[0];
            return forecastDate === eventDateStr;
          });

          if (eventForecasts.length === 0) {
            throw new McpError(
              ErrorCode.InternalError,
              "No forecast data available for the event date"
            );
          }

          // Analyze weather conditions for risks
          const isOutdoor = event_type.toLowerCase().includes("outdoor");
          const isSports = event_type.toLowerCase().includes("sports");
          const isLargeEvent = attendee_count > 500;

          // Check for extreme conditions
          const hasRain = eventForecasts.some((f: any) => 
            f.weather[0].main === "Rain" || f.weather[0].main === "Thunderstorm");
          const hasStrongWind = eventForecasts.some((f: any) => f.wind.speed > 10);
          const hasExtremeTemp = eventForecasts.some((f: any) => 
            f.main.temp > 35 || f.main.temp < 0);

          // Determine risk level
          let riskLevel: "low" | "medium" | "high" = "low";
          const riskFactors = [];
          const recommendations = [];

          if (isOutdoor) {
            if (hasRain) {
              riskLevel = "high";
              riskFactors.push("Precipitation forecast");
              recommendations.push("Prepare covered areas or indoor alternatives");
              recommendations.push("Have a clear cancellation/postponement policy");
            }
            
            if (hasStrongWind) {
              riskLevel = riskLevel === "low" ? "medium" : "high";
              riskFactors.push("Strong winds forecast");
              recommendations.push("Secure all temporary structures and decorations");
              recommendations.push("Have a wind management plan for tents and canopies");
            }
            
            if (hasExtremeTemp) {
              riskLevel = riskLevel === "low" ? "medium" : "high";
              riskFactors.push("Extreme temperature forecast");
              recommendations.push("Provide heating or cooling stations");
              recommendations.push("Ensure adequate hydration options");
            }
          } else {
            // Indoor events have lower weather risks
            if (hasRain && isLargeEvent) {
              riskLevel = "medium";
              riskFactors.push("Rain may affect arrival/departure");
              recommendations.push("Provide covered entry/exit points");
              recommendations.push("Consider transportation challenges for attendees");
            }
          }

          if (isSports) {
            if (hasRain || hasStrongWind) {
              riskLevel = "high";
              riskFactors.push("Weather conditions may affect sports performance and safety");
              recommendations.push("Have clear criteria for safe play conditions");
              recommendations.push("Schedule buffer time for weather delays");
            }
          }

          // Add general recommendations
          recommendations.push("Monitor weather forecasts regularly as the event approaches");
          recommendations.push("Communicate weather expectations to attendees in advance");
          
          if (riskFactors.length === 0) {
            riskFactors.push("No significant weather risks identified");
          }

          const weatherRisk: WeatherRisk = {
            risk_level: riskLevel,
            description: `Weather risk assessment for ${event_type} event in ${location} on ${event_date}: ${riskFactors.join(", ")}`,
            recommendations
          };

          return {
            content: [{
              type: "text",
              text: JSON.stringify(weatherRisk, null, 2)
            }]
          };
        } else {
          // For events beyond forecast range, provide general guidance
          const isOutdoor = event_type.toLowerCase().includes("outdoor");
          const recommendations = [
            "Monitor weather forecasts regularly as the event approaches",
            "Develop contingency plans for various weather scenarios",
            "Consider weather insurance for high-value outdoor events",
            "Plan for seasonal weather patterns typical for the location and time of year"
          ];

          if (isOutdoor) {
            recommendations.push("Have indoor backup options if possible");
            recommendations.push("Prepare for typical weather conditions for that time of year");
          }

          const weatherRisk: WeatherRisk = {
            risk_level: "medium",
            description: `Long-range weather assessment for ${event_type} event in ${location} on ${event_date} (${daysUntilEvent} days away)`,
            recommendations
          };

          return {
            content: [{
              type: "text",
              text: JSON.stringify(weatherRisk, null, 2)
            }]
          };
        }
      } catch (error) {
        if (axios.isAxiosError(error)) {
          throw new McpError(
            ErrorCode.InternalError,
            `Weather API error: ${error.response?.data.message || error.message}`
          );
        }
        throw error;
      }
    }

    default:
      throw new McpError(
        ErrorCode.MethodNotFound,
        `Unknown tool: ${request.params.name}`
      );
  }
});

/**
 * Start the server using stdio transport.
 * This allows the server to communicate via standard input/output streams.
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("OpenWeather MCP server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
