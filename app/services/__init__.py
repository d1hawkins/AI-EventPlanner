"""
Services package for AI Event Planner.

This package contains service classes for managing various aspects
of the application including tenant-aware conversation management.
"""

try:
    from .tenant_conversation_service_with_fallback import TenantConversationService, get_tenant_conversation_service
except ImportError:
    try:
        from .tenant_conversation_service import TenantConversationService, get_tenant_conversation_service
    except ImportError:
        # Fallback if neither service is available
        class TenantConversationService:
            def __init__(self, *args, **kwargs):
                pass
        
        def get_tenant_conversation_service(*args, **kwargs):
            return TenantConversationService()

__all__ = [
    'TenantConversationService',
    'get_tenant_conversation_service'
]
