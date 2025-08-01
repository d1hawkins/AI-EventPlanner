# Azure Application Insights Integration Guide

This guide explains how to use Azure Application Insights with the AI Event Planner application for comprehensive logging, monitoring, and diagnostics.

## Overview

Azure Application Insights is an application performance management (APM) service that helps you monitor your application's performance, track user behavior, and diagnose issues. The AI Event Planner application has been integrated with Azure Application Insights to provide detailed logging and monitoring capabilities for both the SaaS platform and agent components.

## Features

The integration provides the following features:

- **Request Tracking**: All API requests are tracked with detailed information including method, path, status code, and duration.
- **Agent Invocation Logging**: Detailed logs of agent invocations, responses, and errors.
- **Performance Metrics**: Key performance metrics are tracked, such as agent graph execution time and request processing time.
- **Error Tracking**: Comprehensive error tracking with context information and stack traces.
- **State Updates**: Tracking of state changes in the agent system.
- **Custom Events**: Custom events for important operations like agent creation and user interactions.
- **Multi-tenant Support**: All logs include organization ID for multi-tenant environments.
- **Environment Context**: Logs include environment information (development, staging, production).

## Setup

### Prerequisites

- An Azure account with an active subscription
- Azure CLI installed on your machine
- jq installed on your machine (for the setup script)

### Setup Process

1. **Run the Setup Script**:

   ```bash
   ./setup-app-insights.sh
   ```

   This script will:
   - Check if you're logged in to Azure
   - Let you select or create a resource group
   - Create an Application Insights resource
   - Get the instrumentation key
   - Update your .env file with the necessary configuration

2. **Manual Setup**:

   If you prefer to set up Application Insights manually:

   a. Create an Application Insights resource in the Azure portal
   b. Get the instrumentation key
   c. Add the following to your .env file:

   ```
   APPINSIGHTS_INSTRUMENTATIONKEY=your_instrumentation_key
   CLOUD_ROLE=ai-event-planner
   APP_VERSION=1.0.0
   ENVIRONMENT=development  # Options: development, staging, production
   ```

## Configuration Options

The following environment variables can be configured:

- `APPINSIGHTS_INSTRUMENTATIONKEY`: Your Application Insights instrumentation key
- `CLOUD_ROLE`: The role name for your application (default: "ai-event-planner")
- `APP_VERSION`: The version of your application (default: "1.0.0")
- `ENVIRONMENT`: The environment (development, staging, production)

## Viewing Logs and Metrics

Once set up, you can view your application's logs and metrics in the Azure portal:

1. Go to the [Azure portal](https://portal.azure.com)
2. Navigate to your Application Insights resource
3. Use the various sections to explore your data:
   - **Overview**: General metrics and performance
   - **Live Metrics**: Real-time monitoring
   - **Logs**: Query and analyze logs
   - **Failures**: Error analysis
   - **Performance**: Request performance analysis
   - **Availability**: Availability test results
   - **Users**: User behavior analytics

## Common Queries

Here are some useful Kusto queries for analyzing your logs:

### Request Performance

```kusto
requests
| where timestamp > ago(24h)
| summarize count(), avg(duration) by name
| order by avg_duration desc
```

### Agent Invocations

```kusto
customEvents
| where name == "AgentInvocation"
| where timestamp > ago(24h)
| summarize count() by tostring(customDimensions.agent_type)
| order by count_ desc
```

### Error Analysis

```kusto
exceptions
| where timestamp > ago(24h)
| summarize count() by type, method
| order by count_ desc
```

### Performance Metrics

```kusto
customMetrics
| where timestamp > ago(24h)
| where name startswith "agent_"
| summarize avg(value) by name
| order by avg_value desc
```

## Logging in Code

The application uses a centralized logging utility in `app/utils/logging_utils.py`. Here's how to use it in your code:

### Basic Logging

```python
from app.utils.logging_utils import setup_logger

# Set up a logger for your component
logger = setup_logger(
    name="my_component",
    log_level="DEBUG",
    enable_app_insights=True,
    component="my_component"
)

# Use the logger
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Logging with Custom Dimensions

```python
logger.info("User logged in", extra={"custom_dimensions": {
    "user_id": user_id,
    "organization_id": organization_id
}})
```

### Logging Performance Metrics

```python
from app.utils.logging_utils import log_performance_metric

# Log a performance metric
log_performance_metric(
    logger=logger,
    name="my_operation_duration",
    value=duration_ms,
    component="my_component",
    organization_id=organization_id
)
```

### Logging Agent Operations

```python
from app.utils.logging_utils import log_agent_invocation, log_agent_response, log_agent_error

# Log agent invocation
log_agent_invocation(
    logger=logger,
    agent_type="coordinator",
    task="process_message",
    conversation_id=conversation_id,
    organization_id=organization_id
)

# Log agent response
log_agent_response(
    logger=logger,
    agent_type="coordinator",
    response="Agent response text",
    conversation_id=conversation_id,
    organization_id=organization_id
)

# Log agent error
log_agent_error(
    logger=logger,
    agent_type="coordinator",
    error=exception,
    context="Error context",
    conversation_id=conversation_id,
    organization_id=organization_id
)
```

## Best Practices

1. **Use Appropriate Log Levels**:
   - DEBUG: Detailed information for debugging
   - INFO: General information about application progress
   - WARNING: Indication of potential issues
   - ERROR: Error events that might still allow the application to continue
   - CRITICAL: Very severe error events that might cause the application to terminate

2. **Include Context Information**:
   - Always include relevant IDs (user_id, organization_id, conversation_id)
   - Add operation-specific context to help with debugging

3. **Log Performance Metrics**:
   - Log duration for important operations
   - Track resource usage for intensive operations

4. **Handle Sensitive Information**:
   - Never log sensitive information like passwords or tokens
   - Be careful with personal information (consider anonymization)

5. **Use Custom Dimensions**:
   - Add custom dimensions to make logs more searchable and filterable

## Troubleshooting

### No Logs in Application Insights

1. Check that the instrumentation key is correct in your .env file
2. Verify that the Application Insights SDK is properly initialized
3. Make sure logs are being generated at the appropriate level
4. Check for any errors in the console or log files

### High Latency

If logging is causing high latency:

1. Reduce the logging level in production
2. Use sampling to reduce the volume of telemetry
3. Consider batching telemetry items

### Missing Context

If logs are missing context information:

1. Make sure you're passing the correct parameters to logging functions
2. Check that custom dimensions are properly formatted
3. Verify that the logger is properly set up with the component name

## Additional Resources

- [Azure Application Insights Documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Kusto Query Language (KQL) Reference](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Application Insights Python SDK](https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python)
