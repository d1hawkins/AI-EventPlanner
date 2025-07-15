"""
Logging utilities for the event planning system with Azure Application Insights integration.
"""
import os
import logging
import sys
import json
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Union

# Import Application Insights
from applicationinsights import TelemetryClient
from applicationinsights.logging import LoggingHandler

# Define log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Global telemetry client
_telemetry_client = None

def get_telemetry_client() -> Optional[TelemetryClient]:
    """
    Get or create the Application Insights telemetry client.
    
    Returns:
        TelemetryClient instance or None if instrumentation key is not set
    """
    global _telemetry_client
    
    if _telemetry_client is None:
        # Get instrumentation key from environment variable
        instrumentation_key = os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY")
        
        if instrumentation_key:
            _telemetry_client = TelemetryClient(instrumentation_key)
            # Set common properties for all telemetry
            _telemetry_client.context.application.ver = os.getenv("APP_VERSION", "1.0.0")
            _telemetry_client.context.cloud.role = os.getenv("CLOUD_ROLE", "ai-event-planner")
            
            # Set session and user context if available
            if os.getenv("WEBSITE_SITE_NAME"):
                _telemetry_client.context.cloud.role_instance = os.getenv("WEBSITE_SITE_NAME")
                
            # Enable developer mode in non-production environments
            if os.getenv("ENVIRONMENT", "development").lower() != "production":
                _telemetry_client.channel.sender.send_interval_in_milliseconds = 1000
    
    return _telemetry_client

def setup_logger(
    name: str, 
    log_level: str = "INFO", 
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_format: str = DEFAULT_LOG_FORMAT,
    log_file: Optional[str] = None,
    enable_app_insights: bool = True,
    app_insights_level: str = "INFO",
    component: str = None
) -> logging.Logger:
    """
    Set up a logger with file, console, and Application Insights handlers.
    
    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file
        log_to_console: Whether to log to the console
        log_format: Format string for log messages
        log_file: Path to log file (if None, a default name will be used)
        enable_app_insights: Whether to enable Application Insights logging
        app_insights_level: Logging level for Application Insights
        component: Component name for additional context (e.g., "saas", "agent")
        
    Returns:
        Configured logger
    """
    # Get the log level
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    app_insights_level = LOG_LEVELS.get(app_insights_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add file handler if requested
    if log_to_file:
        if log_file is None:
            # Create a default log file name based on the logger name and current date
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = f"logs/{name.lower().replace('.', '_')}_{today}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add Application Insights handler if requested and available
    if enable_app_insights:
        telemetry_client = get_telemetry_client()
        if telemetry_client:
            # Create a custom handler that adds component information
            app_insights_handler = AppInsightsHandler(
                telemetry_client, 
                component_name=component
            )
            app_insights_handler.setLevel(app_insights_level)
            logger.addHandler(app_insights_handler)
    
    return logger


class AppInsightsHandler(LoggingHandler):
    """
    Custom Application Insights logging handler that adds component information.
    """
    
    def __init__(self, telemetry_client, component_name=None):
        """
        Initialize the handler.
        
        Args:
            telemetry_client: Application Insights telemetry client
            component_name: Component name for additional context
        """
        super().__init__(telemetry_client)
        self.component_name = component_name
        
    def emit(self, record):
        """
        Emit a log record to Application Insights.
        
        Args:
            record: Log record
        """
        # Add component name to properties if available
        properties = {
            'custom_dimensions': {
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line_number': record.lineno
            }
        }
        
        if self.component_name:
            properties['custom_dimensions']['component'] = self.component_name
            
        # Add exception info if available
        if record.exc_info:
            properties['custom_dimensions']['exception'] = traceback.format_exception(*record.exc_info)
            
        # Add thread info
        properties['custom_dimensions']['thread'] = record.threadName
        
        # Get the formatted message
        msg = self.format(record)
        
        # Log to Application Insights with appropriate level
        if record.levelno >= logging.ERROR:
            self.client.track_exception(*record.exc_info, properties=properties)
            self.client.track_trace(msg, severity=record.levelname, properties=properties)
        elif record.levelno >= logging.WARNING:
            self.client.track_trace(msg, severity=record.levelname, properties=properties)
        else:
            self.client.track_trace(msg, severity=record.levelname, properties=properties)

def log_agent_invocation(logger: logging.Logger, agent_type: str, task: str, conversation_id: str = None, organization_id: int = None) -> None:
    """
    Log an agent invocation.
    
    Args:
        logger: Logger to use
        agent_type: Type of agent being invoked
        task: Task being delegated to the agent
        conversation_id: Optional conversation ID for tracking
        organization_id: Optional organization ID for tenant context
    """
    properties = {}
    if conversation_id:
        properties["conversation_id"] = conversation_id
    if organization_id:
        properties["organization_id"] = str(organization_id)
    
    logger.info(f"Invoking {agent_type} agent with task: {task}", extra={"custom_dimensions": properties})
    
    # Track as custom event in Application Insights if available
    telemetry_client = get_telemetry_client()
    if telemetry_client:
        event_properties = {
            "agent_type": agent_type,
            "task": task
        }
        if conversation_id:
            event_properties["conversation_id"] = conversation_id
        if organization_id:
            event_properties["organization_id"] = str(organization_id)
            
        telemetry_client.track_event("AgentInvocation", event_properties)
        telemetry_client.flush()

def log_agent_response(logger: logging.Logger, agent_type: str, response: str, conversation_id: str = None, organization_id: int = None) -> None:
    """
    Log an agent response.
    
    Args:
        logger: Logger to use
        agent_type: Type of agent that responded
        response: Response from the agent
        conversation_id: Optional conversation ID for tracking
        organization_id: Optional organization ID for tenant context
    """
    # Truncate long responses for readability
    if len(response) > 500:
        truncated_response = response[:500] + "... [truncated]"
    else:
        truncated_response = response
    
    properties = {}
    if conversation_id:
        properties["conversation_id"] = conversation_id
    if organization_id:
        properties["organization_id"] = str(organization_id)
    
    logger.info(f"Response from {agent_type} agent: {truncated_response}", extra={"custom_dimensions": properties})
    
    # Track as custom event in Application Insights if available
    telemetry_client = get_telemetry_client()
    if telemetry_client:
        event_properties = {
            "agent_type": agent_type,
            "response_length": len(response)
        }
        if conversation_id:
            event_properties["conversation_id"] = conversation_id
        if organization_id:
            event_properties["organization_id"] = str(organization_id)
            
        telemetry_client.track_event("AgentResponse", event_properties)
        telemetry_client.flush()

def log_agent_error(
    logger: logging.Logger, 
    agent_type: str, 
    error: Exception, 
    context: str = "",
    conversation_id: str = None,
    organization_id: int = None
) -> None:
    """
    Log an agent error.
    
    Args:
        logger: Logger to use
        agent_type: Type of agent that encountered an error
        error: The exception that occurred
        context: Additional context about the error
        conversation_id: Optional conversation ID for tracking
        organization_id: Optional organization ID for tenant context
    """
    error_message = f"Error in {agent_type} agent: {str(error)}"
    if context:
        error_message += f" | Context: {context}"
    
    properties = {}
    if conversation_id:
        properties["conversation_id"] = conversation_id
    if organization_id:
        properties["organization_id"] = str(organization_id)
    
    logger.error(error_message, exc_info=True, extra={"custom_dimensions": properties})
    
    # Track as exception in Application Insights if available
    telemetry_client = get_telemetry_client()
    if telemetry_client:
        properties = {
            "agent_type": agent_type,
            "error_type": type(error).__name__
        }
        if context:
            properties["context"] = context
        if conversation_id:
            properties["conversation_id"] = conversation_id
        if organization_id:
            properties["organization_id"] = str(organization_id)
            
        telemetry_client.track_exception(type(error), error, error.__traceback__, properties=properties)
        telemetry_client.flush()

def log_state_update(logger: logging.Logger, state_name: str, state_value: any, conversation_id: str = None, organization_id: int = None) -> None:
    """
    Log a state update.
    
    Args:
        logger: Logger to use
        state_name: Name of the state being updated
        state_value: New value of the state
        conversation_id: Optional conversation ID for tracking
        organization_id: Optional organization ID for tenant context
    """
    properties = {}
    if conversation_id:
        properties["conversation_id"] = conversation_id
    if organization_id:
        properties["organization_id"] = str(organization_id)
    
    # For complex state values, just log that they were updated
    if isinstance(state_value, (dict, list)) and len(str(state_value)) > 100:
        logger.debug(f"Updated {state_name} state (complex value)", extra={"custom_dimensions": properties})
    else:
        logger.debug(f"Updated {state_name} state: {state_value}", extra={"custom_dimensions": properties})
    
    # Track as custom event in Application Insights if available
    telemetry_client = get_telemetry_client()
    if telemetry_client:
        event_properties = {
            "state_name": state_name
        }
        if conversation_id:
            event_properties["conversation_id"] = conversation_id
        if organization_id:
            event_properties["organization_id"] = str(organization_id)
            
        telemetry_client.track_event("StateUpdate", event_properties)
        telemetry_client.flush()

def log_api_request(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: float, user_id: str = None, organization_id: int = None) -> None:
    """
    Log an API request.
    
    Args:
        logger: Logger to use
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user ID
        organization_id: Optional organization ID for tenant context
    """
    properties = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms
    }
    if user_id:
        properties["user_id"] = user_id
    if organization_id:
        properties["organization_id"] = str(organization_id)
    
    logger.info(f"{method} {path} - {status_code} ({duration_ms:.2f}ms)", extra={"custom_dimensions": properties})
    
    # Track as request in Application Insights if available
    telemetry_client = get_telemetry_client()
    if telemetry_client:
        success = 200 <= status_code < 400
        telemetry_client.track_request(f"{method} {path}", path, success, start_time=None, 
                                      duration=duration_ms, response_code=status_code, 
                                      properties=properties)
        telemetry_client.flush()

def log_performance_metric(logger: logging.Logger, name: str, value: float, component: str = None, organization_id: int = None) -> None:
    """
    Log a performance metric.
    
    Args:
        logger: Logger to use
        name: Metric name
        value: Metric value
        component: Optional component name (e.g., "saas", "agent")
        organization_id: Optional organization ID for tenant context
    """
    properties = {
        "metric_name": name,
        "metric_value": value
    }
    if component:
        properties["component"] = component
    if organization_id:
        properties["organization_id"] = str(organization_id)
    
    logger.info(f"Performance metric {name}: {value}", extra={"custom_dimensions": properties})
    
    # Track as metric in Application Insights if available
    telemetry_client = get_telemetry_client()
    if telemetry_client:
        metric_properties = {}
        if component:
            metric_properties["component"] = component
        if organization_id:
            metric_properties["organization_id"] = str(organization_id)
            
        telemetry_client.track_metric(name, value, properties=metric_properties)
        telemetry_client.flush()

def flush_telemetry() -> None:
    """
    Flush any pending telemetry to Application Insights.
    """
    telemetry_client = get_telemetry_client()
    if telemetry_client:
        telemetry_client.flush()
