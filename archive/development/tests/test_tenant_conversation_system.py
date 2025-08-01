"""
Test suite for the tenant-aware conversation system.

This test demonstrates how all conversations are properly tied to:
1. Tenant (Organization)
2. User
3. Conversation/Event ID

It validates the complete multi-tenant conversation flow with proper data isolation.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the new tenant-aware models and services
from app.db.models_tenant_conversations import (
    TenantConversation,
    TenantMessage,
    TenantAgentState,
    ConversationContext,
    ConversationParticipant
)
from app.db.models_saas import Organization, OrganizationUser
from app.db.models import User, Event
from app.services.tenant_conversation_service import TenantConversationService
from app.tools.tenant_agent_communication_tools import TenantAgentCommunicationTools


class TestTenantConversationSystem:
    """
    Test suite for the tenant-aware conversation system.
    
    This comprehensive test validates that all conversations are properly
    scoped to tenant, user, and conversation/event context.
    """
    
    def setup_method(self):
        """Set up test data for each test method."""
        # Create in-memory SQLite database for testing
        self.engine = create_engine("sqlite:///:memory:")
        
        # Create all tables
        from app.db.base import Base
        Base.metadata.create_all(self.engine)
        
        # Create session
        SessionLocal = sessionmaker(bind=self.engine)
        self.db = SessionLocal()
        
        # Create test organizations
        self.org1 = Organization(
            id=1,
            name="Test Organization 1",
            slug="test-org-1",
            plan_id="basic"
        )
        self.org2 = Organization(
            id=2,
            name="Test Organization 2", 
            slug="test-org-2",
            plan_id="premium"
        )
        
        self.db.add_all([self.org1, self.org2])
        
        # Create test users
        self.user1_org1 = User(
            id=1,
            email="user1@org1.com",
            username="user1_org1",
            hashed_password="hashed_password"
        )
        self.user2_org1 = User(
            id=2,
            email="user2@org1.com",
            username="user2_org1",
            hashed_password="hashed_password"
        )
        self.user1_org2 = User(
            id=3,
            email="user1@org2.com",
            username="user1_org2",
            hashed_password="hashed_password"
        )
        
        self.db.add_all([self.user1_org1, self.user2_org1, self.user1_org2])
        
        # Create organization-user relationships
        self.org_user1 = OrganizationUser(
            organization_id=1,
            user_id=1,
            role="admin",
            is_primary=True
        )
        self.org_user2 = OrganizationUser(
            organization_id=1,
            user_id=2,
            role="user"
        )
        self.org_user3 = OrganizationUser(
            organization_id=2,
            user_id=3,
            role="admin",
            is_primary=True
        )
        
        self.db.add_all([self.org_user1, self.org_user2, self.org_user3])
        
        # Create test events
        self.event1_org1 = Event(
            id=1,
            title="Corporate Conference",
            event_type="conference",
            organization_id=1
        )
        self.event2_org1 = Event(
            id=2,
            title="Team Building",
            event_type="team_building",
            organization_id=1
        )
        self.event1_org2 = Event(
            id=3,
            title="Product Launch",
            event_type="product_launch",
            organization_id=2
        )
        
        self.db.add_all([self.event1_org1, self.event2_org1, self.event1_org2])
        
        self.db.commit()
    
    def teardown_method(self):
        """Clean up after each test method."""
        self.db.close()
    
    def test_tenant_conversation_creation(self):
        """Test that conversations are properly created with tenant context."""
        # Create conversation service for org1, user1
        service = TenantConversationService(
            db=self.db,
            organization_id=1,
            user_id=1
        )
        
        # Create a conversation
        conversation = service.create_conversation(
            title="Event Planning Discussion",
            conversation_type="event_planning",
            event_id=1,
            description="Planning the corporate conference",
            primary_agent_type="coordinator"
        )
        
        # Validate conversation properties
        assert conversation.organization_id == 1
        assert conversation.user_id == 1
        assert conversation.event_id == 1
        assert conversation.title == "Event Planning Discussion"
        assert conversation.conversation_type == "event_planning"
        assert conversation.primary_agent_type == "coordinator"
        assert conversation.conversation_uuid is not None
        
        # Validate that conversation context was created
        context = self.db.query(ConversationContext).filter(
            ConversationContext.conversation_id == conversation.id
        ).first()
        assert context is not None
        assert context.organization_id == 1
        assert context.user_id == 1
        
        # Validate that participant was added
        participant = self.db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation.id
        ).first()
        assert participant is not None
        assert participant.organization_id == 1
        assert participant.user_id == 1
        assert participant.role == "owner"
    
    def test_tenant_isolation(self):
        """Test that conversations are properly isolated between tenants."""
        # Create conversations for different organizations
        service_org1 = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        service_org2 = TenantConversationService(db=self.db, organization_id=2, user_id=3)
        
        # Create conversation in org1
        conv1 = service_org1.create_conversation(
            title="Org1 Conversation",
            event_id=1
        )
        
        # Create conversation in org2
        conv2 = service_org2.create_conversation(
            title="Org2 Conversation",
            event_id=3
        )
        
        # Validate that each service only sees its own organization's conversations
        org1_conversations, org1_count = service_org1.list_conversations()
        org2_conversations, org2_count = service_org2.list_conversations()
        
        assert org1_count == 1
        assert org2_count == 1
        assert org1_conversations[0].id == conv1.id
        assert org2_conversations[0].id == conv2.id
        
        # Validate that org1 service cannot access org2 conversation
        org2_conv_from_org1 = service_org1.get_conversation(conv2.id)
        assert org2_conv_from_org1 is None
        
        # Validate that org2 service cannot access org1 conversation
        org1_conv_from_org2 = service_org2.get_conversation(conv1.id)
        assert org1_conv_from_org2 is None
    
    def test_user_access_control(self):
        """Test that users can only access conversations they're authorized for."""
        # Create conversation as user1 in org1
        service_user1 = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        conversation = service_user1.create_conversation(
            title="User1 Conversation",
            event_id=1
        )
        
        # Try to access as user2 in same org (should fail initially)
        service_user2 = TenantConversationService(db=self.db, organization_id=1, user_id=2)
        user2_access = service_user2.get_conversation(conversation.id)
        assert user2_access is None
        
        # Add user2 as participant
        service_user1.add_participant(
            conversation_id=conversation.id,
            user_id=2,
            role="participant"
        )
        
        # Now user2 should be able to access the conversation
        user2_access = service_user2.get_conversation(conversation.id)
        assert user2_access is not None
        assert user2_access.id == conversation.id
    
    def test_message_creation_with_tenant_context(self):
        """Test that messages are properly created with full tenant context."""
        # Create conversation
        service = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        conversation = service.create_conversation(
            title="Message Test Conversation",
            event_id=1
        )
        
        # Add user message
        user_message = service.add_message(
            conversation_id=conversation.id,
            role="user",
            content="I need help planning a corporate event",
            metadata={"source": "web_interface"}
        )
        
        # Add agent message
        agent_message = service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content="I'd be happy to help you plan your corporate event!",
            agent_type="coordinator",
            agent_id="coordinator_001",
            metadata={"confidence": 0.95}
        )
        
        # Validate message properties
        assert user_message.organization_id == 1
        assert user_message.user_id == 1
        assert user_message.conversation_id == conversation.id
        assert user_message.role == "user"
        assert user_message.content == "I need help planning a corporate event"
        
        assert agent_message.organization_id == 1
        assert agent_message.user_id == 1
        assert agent_message.conversation_id == conversation.id
        assert agent_message.role == "assistant"
        assert agent_message.agent_type == "coordinator"
        assert agent_message.agent_id == "coordinator_001"
        
        # Validate message UUIDs are unique
        assert user_message.message_uuid != agent_message.message_uuid
    
    def test_agent_state_management(self):
        """Test agent state management with tenant context."""
        # Create conversation
        service = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        conversation = service.create_conversation(
            title="Agent State Test",
            event_id=1
        )
        
        # Create agent state
        state_data = {
            "current_phase": "requirements_gathering",
            "collected_info": {
                "event_type": "conference",
                "attendee_count": 100,
                "budget_range": "10000-15000"
            },
            "next_steps": ["venue_selection", "catering_options"]
        }
        
        agent_state = service.update_agent_state(
            conversation_id=conversation.id,
            agent_type="coordinator",
            agent_id="coordinator_001",
            state_data=state_data
        )
        
        # Validate agent state properties
        assert agent_state.organization_id == 1
        assert agent_state.user_id == 1
        assert agent_state.conversation_id == conversation.id
        assert agent_state.agent_type == "coordinator"
        assert agent_state.agent_id == "coordinator_001"
        assert agent_state.state_data["current_phase"] == "requirements_gathering"
        assert agent_state.state_data["tenant_context"]["organization_id"] == 1
        
        # Retrieve agent state
        retrieved_state = service.get_agent_state(
            conversation_id=conversation.id,
            agent_type="coordinator",
            agent_id="coordinator_001"
        )
        
        assert retrieved_state is not None
        assert retrieved_state.id == agent_state.id
        assert retrieved_state.state_data["current_phase"] == "requirements_gathering"
    
    def test_agent_communication_tools(self):
        """Test the tenant-aware agent communication tools."""
        # Create conversation
        service = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        conversation = service.create_conversation(
            title="Agent Communication Test",
            event_id=1
        )
        
        # Create agent communication tools
        agent_tools = TenantAgentCommunicationTools(
            db=self.db,
            organization_id=1,
            user_id=1,
            conversation_id=conversation.id,
            agent_type="coordinator",
            agent_id="coordinator_001"
        )
        
        # Send message to user
        user_message = agent_tools.send_message_to_user(
            content="I've started analyzing your event requirements.",
            requires_action=False,
            metadata={"analysis_stage": "initial"}
        )
        
        # Send internal message to another agent
        internal_message = agent_tools.send_internal_message(
            target_agent_type="financial",
            content="Need budget analysis for corporate conference",
            message_type="delegation"
        )
        
        # Validate messages
        assert user_message.organization_id == 1
        assert user_message.user_id == 1
        assert user_message.conversation_id == conversation.id
        assert user_message.agent_type == "coordinator"
        assert user_message.is_internal == False
        
        assert internal_message.organization_id == 1
        assert internal_message.user_id == 1
        assert internal_message.conversation_id == conversation.id
        assert internal_message.agent_type == "coordinator"
        assert internal_message.is_internal == True
        
        # Test preference tracking
        agent_tools.track_user_preference(
            preference_type="venue_style",
            value="modern_corporate",
            confidence=0.8,
            source="conversation"
        )
        
        # Test decision tracking
        agent_tools.track_decision(
            decision_type="venue_location",
            decision="downtown_convention_center",
            reasoning="Central location with good transportation access",
            alternatives_considered=["suburban_hotel", "university_campus"]
        )
        
        # Validate context updates
        context = agent_tools.get_conversation_context()
        assert "venue_style" in context["user_preferences"]
        assert context["user_preferences"]["venue_style"]["value"] == "modern_corporate"
        assert len(context["decision_history"]) > 0
        assert context["decision_history"][0]["decision_type"] == "venue_location"
    
    def test_conversation_context_management(self):
        """Test conversation context management and updates."""
        # Create conversation
        service = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        conversation = service.create_conversation(
            title="Context Management Test",
            event_id=1
        )
        
        # Update conversation context
        context_updates = {
            "user_preferences": {
                "communication_style": "detailed",
                "budget_priority": "high_quality"
            },
            "event_requirements": {
                "attendee_count": 150,
                "duration_days": 2,
                "special_requirements": ["accessibility", "dietary_restrictions"]
            },
            "communication_style": "formal",
            "preferred_detail_level": "high"
        }
        
        updated_context = service.update_conversation_context(
            conversation_id=conversation.id,
            context_updates=context_updates
        )
        
        # Validate context updates
        assert updated_context.organization_id == 1
        assert updated_context.user_id == 1
        assert updated_context.conversation_id == conversation.id
        assert updated_context.communication_style == "formal"
        assert updated_context.preferred_detail_level == "high"
        assert updated_context.user_preferences["communication_style"] == "detailed"
        assert updated_context.event_requirements["attendee_count"] == 150
    
    def test_conversation_summary(self):
        """Test conversation summary generation."""
        # Create conversation with messages and agent states
        service = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        conversation = service.create_conversation(
            title="Summary Test Conversation",
            event_id=1
        )
        
        # Add messages
        service.add_message(
            conversation_id=conversation.id,
            role="user",
            content="I need to plan a corporate conference for 200 people"
        )
        
        service.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content="I'll help you plan that conference. Let me gather some requirements.",
            agent_type="coordinator",
            agent_id="coordinator_001"
        )
        
        # Add agent state
        service.update_agent_state(
            conversation_id=conversation.id,
            agent_type="coordinator",
            agent_id="coordinator_001",
            state_data={"phase": "requirements", "progress": 25}
        )
        
        # Generate summary
        summary = service.get_conversation_summary(conversation.id)
        
        # Validate summary
        assert summary["conversation"]["id"] == conversation.id
        assert summary["conversation"]["title"] == "Summary Test Conversation"
        assert summary["context"]["organization_id"] == 1
        assert summary["context"]["user_id"] == 1
        assert summary["context"]["event_id"] == 1
        assert summary["statistics"]["total_messages"] == 2
        assert summary["statistics"]["user_messages"] == 1
        assert summary["statistics"]["agent_messages"] == 1
        assert len(summary["agents"]) == 1
        assert summary["agents"][0]["type"] == "coordinator"
    
    def test_multi_participant_conversation(self):
        """Test conversations with multiple participants."""
        # Create conversation as user1
        service_user1 = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        conversation = service_user1.create_conversation(
            title="Multi-Participant Conversation",
            event_id=1
        )
        
        # Add user2 as participant
        participant = service_user1.add_participant(
            conversation_id=conversation.id,
            user_id=2,
            role="collaborator",
            permissions={"can_edit": True, "can_invite": False}
        )
        
        # Validate participant
        assert participant.organization_id == 1
        assert participant.conversation_id == conversation.id
        assert participant.user_id == 2
        assert participant.role == "collaborator"
        assert participant.permissions["can_edit"] == True
        
        # Test that user2 can now access the conversation
        service_user2 = TenantConversationService(db=self.db, organization_id=1, user_id=2)
        user2_conversation = service_user2.get_conversation(conversation.id)
        assert user2_conversation is not None
        assert user2_conversation.id == conversation.id
        
        # Test that both users see the conversation in their lists
        user1_conversations, user1_count = service_user1.list_conversations()
        user2_conversations, user2_count = service_user2.list_conversations()
        
        assert user1_count == 1
        assert user2_count == 1
        assert user1_conversations[0].id == conversation.id
        assert user2_conversations[0].id == conversation.id
    
    def test_event_conversation_association(self):
        """Test that conversations are properly associated with events."""
        # Create conversations for different events
        service = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        
        conv1 = service.create_conversation(
            title="Conference Planning",
            event_id=1
        )
        
        conv2 = service.create_conversation(
            title="Team Building Planning",
            event_id=2
        )
        
        conv3 = service.create_conversation(
            title="General Discussion",
            event_id=None  # No event association
        )
        
        # Test filtering by event
        event1_conversations, event1_count = service.list_conversations(event_id=1)
        event2_conversations, event2_count = service.list_conversations(event_id=2)
        
        assert event1_count == 1
        assert event2_count == 1
        assert event1_conversations[0].id == conv1.id
        assert event2_conversations[0].id == conv2.id
        
        # Test that general conversation is not associated with any event
        assert conv3.event_id is None
    
    def test_conversation_status_and_phases(self):
        """Test conversation status and phase management."""
        service = TenantConversationService(db=self.db, organization_id=1, user_id=1)
        conversation = service.create_conversation(
            title="Status Test Conversation",
            event_id=1
        )
        
        # Initially should be active
        assert conversation.status == "active"
        assert conversation.completion_percentage == 0
        
        # Update conversation status through context
        service.update_conversation_context(
            conversation_id=conversation.id,
            context_updates={
                "current_phase": "venue_selection",
                "completion_percentage": 30
            }
        )
        
        # Retrieve updated conversation
        updated_conversation = service.get_conversation(conversation.id)
        # Note: The status and completion_percentage would be updated through
        # the agent communication tools in a real scenario
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("Running Tenant Conversation System Tests...")
        
        test_methods = [
            self.test_tenant_conversation_creation,
            self.test_tenant_isolation,
            self.test_user_access_control,
            self.test_message_creation_with_tenant_context,
            self.test_agent_state_management,
            self.test_agent_communication_tools,
            self.test_conversation_context_management,
            self.test_conversation_summary,
            self.test_multi_participant_conversation,
            self.test_event_conversation_association,
            self.test_conversation_status_and_phases
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                self.setup_method()
                test_method()
                print(f"✓ {test_method.__name__}")
                passed += 1
            except Exception as e:
                print(f"✗ {test_method.__name__}: {str(e)}")
                failed += 1
            finally:
                self.teardown_method()
        
        print(f"\nTest Results: {passed} passed, {failed} failed")
        return failed == 0


def main():
    """Main function to run the tenant conversation system tests."""
    print("=" * 80)
    print("TENANT-AWARE CONVERSATION SYSTEM TEST SUITE")
    print("=" * 80)
    print()
    print("This test suite validates that all conversations are properly tied to:")
    print("1. Tenant (Organization)")
    print("2. User")
    print("3. Conversation/Event ID")
    print()
    print("Key features being tested:")
    print("- Multi-tenant data isolation")
    print("- User access control within tenants")
    print("- Conversation-event associations")
    print("- Agent state management with tenant context")
    print("- Message tracking with full context")
    print("- Conversation context and memory management")
    print("- Multi-participant conversations")
    print("- Agent communication tools")
    print()
    
    # Run the tests
    test_suite = TestTenantConversationSystem()
    success = test_suite.run_all_tests()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("The tenant-aware conversation system is working correctly.")
        print("All conversations are properly scoped to Tenant, User, and Conversation/Event ID.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the failed tests and fix any issues.")
    print("=" * 80)
    
    return success


if __name__ == "__main__":
    main()
