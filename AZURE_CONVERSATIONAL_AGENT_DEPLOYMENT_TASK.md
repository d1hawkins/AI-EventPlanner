# Azure Conversational Agent Deployment Task
## Deploy Enhanced Conversational Flow to Azure Production

**Created**: 2025-06-28  
**Priority**: High  
**Estimated Time**: 4-6 hours  
**Status**: Ready to Execute  

---

## 📋 Executive Summary

### Problem Statement
The conversational agent improvements have been successfully implemented locally but are not reflected in the Azure deployment. The current Azure deployment uses a simplified embedded agent logic instead of the sophisticated conversational flow with question management, recommendations, and proactive suggestions.

### Root Cause Analysis
1. **Missing Components**: The deployment script `azure-deploy-complete-saas-with-agents.sh` only copies basic files and doesn't include the full `app/` directory structure
2. **Standalone App Logic**: `app_adapter_standalone.py` uses embedded simple agent logic instead of the real conversational coordinator graph
3. **Missing Dependencies**: Conversational utilities are not included in the deployment package

### Solution Overview
Update the Azure deployment to include all conversational agent components and integrate them properly with the standalone application.

---

## 🎯 Implementation Plan

### Phase 1: Update Deployment Script (Priority: Critical)
**Estimated Time**: 2-3 hours

### Phase 2: Create Conversational-Enabled Main App (Priority: High)
**Estimated Time**: 1-2 hours

### Phase 3: Testing & Validation (Priority: High)
**Estimated Time**: 1-2 hours

---

## 📝 Detailed Task Breakdown

## Phase 1: Update Azure Deployment Script

### Task 1.1: Backup Current Deployment Script
**File**: `azure-deploy-complete-saas-with-agents.sh`  
**Status**: ⏳ Not Started  
**Estimated Time**: 15 minutes  

#### Subtasks:
- [ ] Create backup of current deployment script
- [ ] Document current deployment behavior for rollback reference

#### Implementation:
```bash
# Create backup
cp azure-deploy-complete-saas-with-agents.sh azure-deploy-complete-saas-with-agents.sh.backup

# Document current behavior
echo "Backup created on $(date)" >> DEPLOYMENT_BACKUP_LOG.md
```

### Task 1.2: Update File Copying Section
**File**: `azure-deploy-complete-saas-with-agents.sh`  
**Status**: ⏳ Not Started  
**Estimated Time**: 45 minutes  

#### Subtasks:
- [ ] Add copying of entire `app/` directory structure
- [ ] Include all conversational utility files
- [ ] Copy updated coordinator graph
- [ ] Include agent tools and schemas

#### Implementation Details:
```bash
# Add to deployment script after "Copying application files..."
print_status "Copying conversational agent components..."

# Copy entire app directory structure
cp -r app/ $DEPLOY_DIR/app/

# Ensure all conversational utilities are included
mkdir -p $DEPLOY_DIR/app/utils
cp app/utils/question_manager.py $DEPLOY_DIR/app/utils/
cp app/utils/recommendation_engine.py $DEPLOY_DIR/app/utils/
cp app/utils/conversation_memory.py $DEPLOY_DIR/app/utils/
cp app/utils/conversation_paths.py $DEPLOY_DIR/app/utils/
cp app/utils/proactive_suggestions.py $DEPLOY_DIR/app/utils/
cp app/utils/recommendation_learning.py $DEPLOY_DIR/app/utils/

# Copy updated coordinator graph
mkdir -p $DEPLOY_DIR/app/graphs
cp app/graphs/coordinator_graph.py $DEPLOY_DIR/app/graphs/

# Copy agent tools and schemas
mkdir -p $DEPLOY_DIR/app/tools
cp -r app/tools/ $DEPLOY_DIR/app/tools/
mkdir -p $DEPLOY_DIR/app/schemas
cp -r app/schemas/ $DEPLOY_DIR/app/schemas/

print_success "Conversational agent components copied"
```

### Task 1.3: Add Environment Variables for Conversational Mode
**File**: `azure-deploy-complete-saas-with-agents.sh`  
**Status**: ⏳ Not Started  
**Estimated Time**: 30 minutes  

#### Subtasks:
- [ ] Add conversational mode environment variables
- [ ] Configure recommendation engine settings
- [ ] Set conversation feature flags

#### Implementation Details:
```bash
# Add to environment variables section
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    USE_REAL_AGENTS=true \
    LLM_PROVIDER=google \
    GOOGLE_MODEL=gemini-2.0-flash \
    GOOGLE_API_KEY=$GOOGLE_API_KEY \
    CONVERSATION_MODE=enabled \
    RECOMMENDATION_ENGINE=enabled \
    QUESTION_FLOW=conversational \
    CONVERSATION_MEMORY_LIMIT=50 \
    ENABLE_PROACTIVE_SUGGESTIONS=true \
    CONVERSATION_FEATURE_FLAG=true \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true \
    > /dev/null
```

### Task 1.4: Update Testing Section
**File**: `azure-deploy-complete-saas-with-agents.sh`  
**Status**: ⏳ Not Started  
**Estimated Time**: 45 minutes  

#### Subtasks:
- [ ] Add conversational flow testing
- [ ] Test one-question-at-a-time behavior
- [ ] Validate recommendation engine responses
- [ ] Test conversation state persistence

#### Implementation Details:
```bash
# Add conversational flow testing function
test_conversational_flow() {
    print_status "Testing conversational flow..."
    
    # Test initial question
    initial_response=$(curl -s -X POST "$APP_URL/api/agents/message" \
        -H "Content-Type: application/json" \
        -d '{"agent_type": "coordinator", "message": "I want to plan an event"}' \
        2>/dev/null || echo "{}")
    
    if echo "$initial_response" | grep -q '"conversation_stage": *"discovery"'; then
        print_success "Conversational discovery mode is active"
    else
        print_error "Conversational mode not detected"
        echo "Response: $initial_response"
    fi
    
    # Test recommendation engine
    if echo "$initial_response" | grep -q '"recommendations"'; then
        print_success "Recommendation engine is working"
    else
        print_warning "Recommendation engine may not be active"
    fi
    
    # Test question flow
    if echo "$initial_response" | grep -q '"current_question_focus"'; then
        print_success "Question management system is active"
    else
        print_warning "Question management system may not be working"
    fi
}

# Add to main testing section
test_conversational_flow
```

## Phase 2: Create Conversational-Enabled Main App

### Task 2.1: Create New Main Application File
**File**: `app_adapter_conversational.py` (new file)  
**Status**: ⏳ Not Started  
**Estimated Time**: 60 minutes  

#### Subtasks:
- [ ] Create new main application file that uses real coordinator
- [ ] Import conversational agent components
- [ ] Integrate with Azure ASGI requirements
- [ ] Add proper error handling and fallbacks

#### Implementation Details:
```python
#!/usr/bin/env python3
"""
Conversational Azure adapter with full agent functionality - ASGI Compatible
This version uses the real conversational coordinator graph
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

# Add paths for Azure deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))

# Azure wwwroot path
wwwroot_dir = '/home/site/wwwroot'
if os.path.exists(wwwroot_dir):
    sys.path.insert(0, wwwroot_dir)

print("🚀 Starting conversational agent adapter (ASGI)...")

# Environment configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyBgdKgwJYyQTJEWDY08roJwc-hFxwxXwOU')
USE_REAL_AGENTS = os.getenv('USE_REAL_AGENTS', 'true').lower() == 'true'
CONVERSATION_MODE = os.getenv('CONVERSATION_MODE', 'enabled').lower() == 'enabled'

# Import conversational coordinator
try:
    from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state
    from app.utils.question_manager import QuestionManager
    from app.utils.recommendation_engine import RecommendationEngine
    CONVERSATIONAL_AVAILABLE = True
    print("✅ Conversational coordinator imported successfully")
except Exception as e:
    print(f"❌ Failed to import conversational coordinator: {e}")
    CONVERSATIONAL_AVAILABLE = False

# Global coordinator graph
coordinator_graph = None
if CONVERSATIONAL_AVAILABLE:
    try:
        coordinator_graph = create_coordinator_graph()
        print("✅ Conversational coordinator graph created")
    except Exception as e:
        print(f"❌ Failed to create coordinator graph: {e}")
        coordinator_graph = None

async def get_conversational_response(agent_type: str, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Get response using the conversational coordinator graph"""
    try:
        if not coordinator_graph:
            raise Exception("Coordinator graph not available")
        
        # Create or load conversation state
        state = create_initial_state()
        
        # Add user message to state
        state["messages"].append({
            "role": "user",
            "content": message
        })
        
        # Run the coordinator graph
        result = await asyncio.to_thread(coordinator_graph.invoke, state)
        
        # Extract the last assistant message
        assistant_messages = [msg for msg in result["messages"] if msg["role"] == "assistant"]
        if assistant_messages:
            response_text = assistant_messages[-1]["content"]
        else:
            response_text = "I'm here to help you plan your event. Could you tell me more about what you have in mind?"
        
        return {
            "response": response_text,
            "conversation_id": conversation_id or f"conv_{agent_type}_{int(datetime.now().timestamp())}",
            "agent_type": agent_type,
            "conversation_stage": result.get("conversation_stage", "discovery"),
            "current_question_focus": result.get("current_question_focus"),
            "using_real_agent": True,
            "using_conversational_flow": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in conversational response: {e}")
        # Fallback to simple response
        return {
            "response": f"I'm the {agent_type} agent. I encountered an issue but I'm here to help with your event planning. Could you please rephrase your question?",
            "conversation_id": conversation_id or f"conv_{agent_type}_fallback",
            "agent_type": agent_type,
            "using_real_agent": False,
            "using_conversational_flow": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Rest of ASGI application code...
```

### Task 2.2: Update Deployment Script to Use New Main App
**File**: `azure-deploy-complete-saas-with-agents.sh`  
**Status**: ⏳ Not Started  
**Estimated Time**: 15 minutes  

#### Subtasks:
- [ ] Update deployment script to copy new main application file
- [ ] Update web.config to use new main app

#### Implementation Details:
```bash
# Replace in deployment script
cp app_adapter_conversational.py $DEPLOY_DIR/

# Update web.config
cat > $DEPLOY_DIR/web.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" arguments="app_adapter_conversational.py" stdoutLogEnabled="true" stdoutLogFile="python.log" startupTimeLimit="60" requestTimeout="00:04:00">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
        <environmentVariable name="USE_REAL_AGENTS" value="true" />
        <environmentVariable name="CONVERSATION_MODE" value="enabled" />
        <environmentVariable name="LLM_PROVIDER" value="google" />
        <environmentVariable name="GOOGLE_MODEL" value="gemini-2.0-flash" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
EOF
```

## Phase 3: Testing & Validation

### Task 3.1: Local Testing Before Deployment
**Status**: ⏳ Not Started  
**Estimated Time**: 30 minutes  

#### Subtasks:
- [ ] Test new main application locally
- [ ] Verify conversational flow works
- [ ] Test all conversational utilities import correctly
- [ ] Validate ASGI compatibility

#### Implementation:
```bash
# Test locally
python app_adapter_conversational.py

# Test conversational endpoint
curl -X POST "http://localhost:8000/api/agents/message" \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "coordinator", "message": "I want to plan a corporate event"}'
```

### Task 3.2: Deploy and Test in Azure
**Status**: ⏳ Not Started  
**Estimated Time**: 45 minutes  

#### Subtasks:
- [ ] Run updated deployment script
- [ ] Monitor deployment logs
- [ ] Test conversational flow in Azure
- [ ] Verify all components are working

#### Implementation:
```bash
# Deploy with updated script
./azure-deploy-complete-saas-with-agents.sh

# Test conversational flow
curl -X POST "https://ai-event-planner-saas-py.azurewebsites.net/api/agents/message" \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "coordinator", "message": "I want to plan an event"}'
```

### Task 3.3: Comprehensive Testing Suite
**Status**: ⏳ Not Started  
**Estimated Time**: 45 minutes  

#### Subtasks:
- [ ] Test one-question-at-a-time flow
- [ ] Verify recommendations are provided
- [ ] Test conversation memory
- [ ] Validate proactive suggestions
- [ ] Test all agent types

#### Test Cases:
1. **Initial Conversation**: User says "I want to plan an event" → Should get single question about event type
2. **Follow-up Questions**: Answer should trigger next logical question
3. **Recommendations**: Questions should include relevant recommendations
4. **Proposal Generation**: After sufficient info, should offer to create proposal
5. **Error Handling**: Invalid inputs should be handled gracefully

---

## 🔧 Technical Implementation Details

### Key Files to Modify:
1. **`azure-deploy-complete-saas-with-agents.sh`** - Main deployment script
2. **`app_adapter_conversational.py`** - New conversational main application (new)
3. **Environment variables** - Azure App Service configuration

### Dependencies Already Available:
- All conversational utilities exist in `app/utils/`
- Updated coordinator graph in `app/graphs/coordinator_graph.py`
- All required agent tools and schemas

### No New External Dependencies Required:
- Uses existing LangChain and LangGraph infrastructure
- All conversational components are already implemented

---

## 🚨 Risk Management

### Potential Issues:
1. **Import Errors**: Conversational utilities may not import correctly in Azure
2. **Memory Usage**: Full app structure may increase memory usage
3. **Startup Time**: Additional imports may slow startup
4. **Compatibility**: ASGI compatibility with conversational components

### Mitigation Strategies:
1. **Fallback Logic**: Include fallback to simple agent if conversational fails
2. **Error Handling**: Comprehensive try/catch blocks around imports
3. **Monitoring**: Enhanced logging to track conversational flow
4. **Rollback Plan**: Keep backup of working deployment script

---

## 📊 Success Criteria

### Functional Requirements:
- [ ] Agent asks one question at a time instead of batch collection
- [ ] Questions include relevant recommendations
- [ ] Conversation flows naturally from discovery to proposal
- [ ] Proactive suggestions are provided when appropriate
- [ ] All conversational utilities work correctly

### Technical Requirements:
- [ ] Application starts successfully in Azure
- [ ] No import errors in deployment logs
- [ ] Response time < 5 seconds per question
- [ ] Memory usage within acceptable limits
- [ ] All API endpoints respond correctly

### User Experience Requirements:
- [ ] Natural conversation flow (not overwhelming)
- [ ] Helpful recommendations provided
- [ ] Clear progression through event planning stages
- [ ] Professional and engaging tone
- [ ] Error messages are user-friendly

---

## 🔄 Rollback Strategy

### If Deployment Fails:
1. **Immediate Rollback**:
   ```bash
   # Restore backup deployment script
   cp azure-deploy-complete-saas-with-agents.sh.backup azure-deploy-complete-saas-with-agents.sh
   
   # Redeploy with original script
   ./azure-deploy-complete-saas-with-agents.sh
   ```

2. **Environment Variable Rollback**:
   ```bash
   # Disable conversational mode
   az webapp config appsettings set \
       --resource-group ai-event-planner-rg \
       --name ai-event-planner-saas-py \
       --settings CONVERSATION_MODE=disabled
   ```

### If Partial Functionality:
1. **Feature Flag Disable**: Set `CONVERSATION_FEATURE_FLAG=false`
2. **Fallback Mode**: Application will use embedded simple logic
3. **Gradual Rollout**: Enable for subset of users first

---

## 📋 Execution Checklist

### Pre-Deployment:
- [ ] Backup current deployment script
- [ ] Test new main application locally
- [ ] Verify all conversational utilities are present
- [ ] Review Azure resource limits

### Deployment:
- [ ] Update deployment script with conversational components
- [ ] Create new conversational main application
- [ ] Set environment variables for conversational mode
- [ ] Deploy to Azure
- [ ] Monitor deployment logs

### Post-Deployment:
- [ ] Test health endpoint
- [ ] Test conversational flow
- [ ] Verify recommendations are working
- [ ] Check application logs for errors
- [ ] Monitor performance metrics

### Validation:
- [ ] Complete end-to-end conversation test
- [ ] Verify all agent types work
- [ ] Test error handling scenarios
- [ ] Confirm user experience improvements

---

## 📞 Support and Monitoring

### Monitoring Points:
1. **Application Insights**: Track conversational metrics
2. **Response Times**: Monitor question response times
3. **Error Rates**: Track conversational flow errors
4. **User Engagement**: Measure conversation completion rates

### Key Metrics to Track:
- Average conversation length
- Question response time
- Recommendation relevance
- User satisfaction indicators
- Error rates by conversation stage

### Alerting:
- Set up alerts for conversational flow failures
- Monitor memory usage increases
- Track response time degradation
- Alert on import errors

---

**Last Updated**: 2025-06-28  
**Next Review**: After deployment completion  
**Document Version**: 1.0  
**Estimated Total Time**: 4-6 hours  
**Priority**: High - Critical for user experience improvement
