"""
Agent Router - Compatibility layer for deployment scripts
This file provides backward compatibility by importing from api_router.py
"""

# Import all functions from api_router for backward compatibility
from .api_router import *

# Ensure all expected functions are available
__all__ = [
    'get_agent_response',
    'get_conversation_history', 
    'list_conversations',
    'delete_conversation'
]
