"""
Logging utilities for the event planning system.
"""
import os
import logging
import sys
from datetime import datetime
from typing import Optional

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

def setup_logger(
    name: str, 
    log_level: str = "INFO", 
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_format: str = DEFAULT_LOG_FORMAT,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file
        log_to_console: Whether to log to the console
        log_format: Format string for log messages
        log_file: Path to log file (if None, a default name will be used)
        
    Returns:
        Configured logger
    """
    # Get the log level
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    
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
    
    return logger

def log_agent_invocation(logger: logging.Logger, agent_type: str, task: str) -> None:
    """
    Log an agent invocation.
    
    Args:
        logger: Logger to use
        agent_type: Type of agent being invoked
        task: Task being delegated to the agent
    """
    logger.info(f"Invoking {agent_type} agent with task: {task}")

def log_agent_response(logger: logging.Logger, agent_type: str, response: str) -> None:
    """
    Log an agent response.
    
    Args:
        logger: Logger to use
        agent_type: Type of agent that responded
        response: Response from the agent
    """
    # Truncate long responses for readability
    if len(response) > 500:
        truncated_response = response[:500] + "... [truncated]"
    else:
        truncated_response = response
    
    logger.info(f"Response from {agent_type} agent: {truncated_response}")

def log_agent_error(
    logger: logging.Logger, 
    agent_type: str, 
    error: Exception, 
    context: str = ""
) -> None:
    """
    Log an agent error.
    
    Args:
        logger: Logger to use
        agent_type: Type of agent that encountered an error
        error: The exception that occurred
        context: Additional context about the error
    """
    error_message = f"Error in {agent_type} agent: {str(error)}"
    if context:
        error_message += f" | Context: {context}"
    
    logger.error(error_message, exc_info=True)

def log_state_update(logger: logging.Logger, state_name: str, state_value: any) -> None:
    """
    Log a state update.
    
    Args:
        logger: Logger to use
        state_name: Name of the state being updated
        state_value: New value of the state
    """
    # For complex state values, just log that they were updated
    if isinstance(state_value, (dict, list)) and len(str(state_value)) > 100:
        logger.debug(f"Updated {state_name} state (complex value)")
    else:
        logger.debug(f"Updated {state_name} state: {state_value}")
