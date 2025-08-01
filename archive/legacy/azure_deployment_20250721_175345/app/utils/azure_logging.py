"""
Enhanced logging for Azure agent deployment.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configure Azure-specific logging
def setup_azure_logging():
    """Setup logging configuration for Azure environment"""
    
    # Create logger
    logger = logging.getLogger('azure_agents')
    logger.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for Azure
    if os.path.exists('/home/site/wwwroot'):
        file_handler = logging.FileHandler('/home/site/wwwroot/agent_logs.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_import_attempt(logger, module_name: str, strategy: str, success: bool, error: Optional[str] = None):
    """Log import attempt with details"""
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'module': module_name,
        'strategy': strategy,
        'success': success,
        'error': error
    }
    
    if success:
        logger.info(f"Import successful: {module_name} using {strategy}")
    else:
        logger.error(f"Import failed: {module_name} using {strategy} - {error}")

def log_agent_status(logger, agent_type: str, status: str, details: Optional[Dict[str, Any]] = None):
    """Log agent availability status"""
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'agent_type': agent_type,
        'status': status,
        'details': details or {}
    }
    
    logger.info(f"Agent status: {agent_type} - {status}")

def log_fallback_usage(logger, agent_type: str, reason: str, usage_count: int):
    """Log when fallback system is used"""
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'agent_type': agent_type,
        'reason': reason,
        'usage_count': usage_count
    }
    
    logger.warning(f"Fallback used: {agent_type} - {reason} (count: {usage_count})")

def log_deployment_status(logger, status: str, details: Dict[str, Any]):
    """Log overall deployment status"""
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'deployment_status': status,
        'details': details
    }
    
    if status == 'success':
        logger.info(f"Deployment successful: {details}")
    else:
        logger.error(f"Deployment issues: {details}")

def log_health_check(logger, health_status: Dict[str, Any]):
    """Log health check results"""
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'health_status': health_status
    }
    
    overall_status = health_status.get('status', 'unknown')
    
    if overall_status == 'healthy':
        logger.info(f"Health check passed: {health_status}")
    elif overall_status == 'degraded':
        logger.warning(f"Health check degraded: {health_status}")
    else:
        logger.error(f"Health check failed: {health_status}")

def log_diagnostic_report(logger, diagnostic_report: Dict[str, Any]):
    """Log diagnostic report results"""
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'diagnostic_report': diagnostic_report
    }
    
    failed_imports = diagnostic_report.get('failed_imports', [])
    missing_modules = diagnostic_report.get('missing_modules', [])
    
    if not failed_imports and not missing_modules:
        logger.info(f"Diagnostic report clean: {diagnostic_report}")
    else:
        logger.error(f"Diagnostic report shows issues: failed_imports={failed_imports}, missing_modules={missing_modules}")

def create_structured_log_entry(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a structured log entry for Azure Application Insights"""
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'environment': 'azure' if os.path.exists('/home/site/wwwroot') else 'local',
        'data': data
    }

def log_performance_metrics(logger, operation: str, duration_ms: float, success: bool, details: Optional[Dict[str, Any]] = None):
    """Log performance metrics for operations"""
    
    log_data = create_structured_log_entry('performance_metric', {
        'operation': operation,
        'duration_ms': duration_ms,
        'success': success,
        'details': details or {}
    })
    
    if success:
        logger.info(f"Performance: {operation} completed in {duration_ms}ms")
    else:
        logger.warning(f"Performance: {operation} failed after {duration_ms}ms")

def log_azure_environment_info(logger):
    """Log Azure environment information for debugging"""
    
    env_info = {
        'python_version': os.sys.version,
        'python_path': os.sys.path[:10],  # First 10 paths
        'environment_variables': {
            'WEBSITE_SITE_NAME': os.getenv('WEBSITE_SITE_NAME'),
            'WEBSITE_RESOURCE_GROUP': os.getenv('WEBSITE_RESOURCE_GROUP'),
            'WEBSITE_OWNER_NAME': os.getenv('WEBSITE_OWNER_NAME'),
            'PYTHONPATH': os.getenv('PYTHONPATH'),
            'HOME': os.getenv('HOME'),
            'WEBSITE_HOSTNAME': os.getenv('WEBSITE_HOSTNAME')
        },
        'file_system': {
            'wwwroot_exists': os.path.exists('/home/site/wwwroot'),
            'app_dir_exists': os.path.exists('/home/site/wwwroot/app'),
            'agents_dir_exists': os.path.exists('/home/site/wwwroot/app/agents'),
            'graphs_dir_exists': os.path.exists('/home/site/wwwroot/app/graphs')
        }
    }
    
    log_data = create_structured_log_entry('environment_info', env_info)
    logger.info(f"Azure environment info: {env_info}")

# Global logger instance
azure_logger = None

def get_azure_logger():
    """Get or create the global Azure logger"""
    global azure_logger
    if azure_logger is None:
        azure_logger = setup_azure_logging()
        log_azure_environment_info(azure_logger)
    return azure_logger
