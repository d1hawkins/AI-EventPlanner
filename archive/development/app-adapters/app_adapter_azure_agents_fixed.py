#!/usr/bin/env python3
"""
Enhanced Azure App Adapter with Robust Import Strategy
Fixes Azure agent import issues to enable real agents instead of mock responses.
"""

import os
import sys
import importlib
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables to track import status
REAL_AGENTS_AVAILABLE = False
IMPORT_STRATEGY_USED = None
FAILED_IMPORTS = []
MISSING_MODULES = []
IMPORTED_MODULES = {}

# Enhanced import strategies with Azure-specific paths
IMPORT_STRATEGIES = [
    # Strategy 1: Direct imports (works locally)
    {
        'name': 'direct_import',
        'paths': {
            'router': 'app.agents.api_router',
            'factory': 'app.agents.agent_factory',
            'session': 'app.db.session',
            'tenant': 'app.middleware.tenant',
            'coordinator_graph': 'app.graphs.coordinator_graph',
            'resource_planning_graph': 'app.graphs.resource_planning_graph',
            'financial_graph': 'app.graphs.financial_graph',
            'stakeholder_graph': 'app.graphs.stakeholder_management_graph',
            'marketing_graph': 'app.graphs.marketing_communications_graph',
            'project_graph': 'app.graphs.project_management_graph',
            'analytics_graph': 'app.graphs.analytics_graph',
            'compliance_graph': 'app.graphs.compliance_security_graph'
        }
    },
    # Strategy 2: Azure wwwroot paths
    {
        'name': 'azure_wwwroot',
        'paths': {
            'router': 'app.agents.api_router',
            'factory': 'app.agents.agent_factory',
            'session': 'app.db.session',
            'tenant': 'app.middleware.tenant',
            'coordinator_graph': 'app.graphs.coordinator_graph',
            'resource_planning_graph': 'app.graphs.resource_planning_graph',
            'financial_graph': 'app.graphs.financial_graph',
            'stakeholder_graph': 'app.graphs.stakeholder_management_graph',
            'marketing_graph': 'app.graphs.marketing_communications_graph',
            'project_graph': 'app.graphs.project_management_graph',
            'analytics_graph': 'app.graphs.analytics_graph',
            'compliance_graph': 'app.graphs.compliance_security_graph'
        },
        'sys_path_additions': ['/home/site/wwwroot', '/home/site/wwwroot/app']
    },
    # Strategy 3: Relative imports
    {
        'name': 'relative_import',
        'paths': {
            'router': 'agents.api_router',
            'factory': 'agents.agent_factory',
            'session': 'db.session',
            'tenant': 'middleware.tenant',
            'coordinator_graph': 'graphs.coordinator_graph',
            'resource_planning_graph': 'graphs.resource_planning_graph',
            'financial_graph': 'graphs.financial_graph',
            'stakeholder_graph': 'graphs.stakeholder_management_graph',
            'marketing_graph': 'graphs.marketing_communications_graph',
            'project_graph': 'graphs.project_management_graph',
            'analytics_graph': 'graphs.analytics_graph',
            'compliance_graph': 'graphs.compliance_security_graph'
        }
    },
    # Strategy 4: Azure-specific absolute paths
    {
        'name': 'azure_absolute',
        'paths': {
            'router': 'site.wwwroot.app.agents.api_router',
            'factory': 'site.wwwroot.app.agents.agent_factory',
            'session': 'site.wwwroot.app.db.session',
            'tenant': 'site.wwwroot.app.middleware.tenant',
            'coordinator_graph': 'site.wwwroot.app.graphs.coordinator_graph',
            'resource_planning_graph': 'site.wwwroot.app.graphs.resource_planning_graph',
            'financial_graph': 'site.wwwroot.app.graphs.financial_graph',
            'stakeholder_graph': 'site.wwwroot.app.graphs.stakeholder_management_graph',
            'marketing_graph': 'site.wwwroot.app.graphs.marketing_communications_graph',
            'project_graph': 'site.wwwroot.app.graphs.project_management_graph',
            'analytics_graph': 'site.wwwroot.app.graphs.analytics_graph',
            'compliance_graph': 'site.wwwroot.app.graphs.compliance_security_graph'
        }
    }
]

def setup_azure_python_path():
    """Configure Python path for Azure environment"""
    azure_paths = [
        '/home/site/wwwroot',
        '/home/site/wwwroot/app',
        '/home/site/wwwroot/app/agents',
        '/home/site/wwwroot/app/graphs',
        '/home/site/wwwroot/app/tools',
        '/home/site/wwwroot/app/utils',
        '/home/site/wwwroot/app/db',
        '/home/site/wwwroot/app/middleware'
    ]
    
    for path in azure_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
            logger.info(f"Added to Python path: {path}")

def log_import_attempt(module_name: str, strategy: str, success: bool, error: Optional[str] = None):
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
        FAILED_IMPORTS.append(log_data)

def try_import_strategy(strategy: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Attempt import with specific strategy"""
    global IMPORTED_MODULES
    
    logger.info(f"Trying import strategy: {strategy['name']}")
    
    # Add sys path additions if specified
    if 'sys_path_additions' in strategy:
        for path in strategy['sys_path_additions']:
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(0, path)
                logger.info(f"Added to Python path: {path}")
    
    imported_modules = {}
    failed_modules = []
    
    for module_key, module_path in strategy['paths'].items():
        try:
            module = importlib.import_module(module_path)
            imported_modules[module_key] = module
            log_import_attempt(module_path, strategy['name'], True)
            logger.info(f"Successfully imported {module_key}: {module_path}")
        except Exception as e:
            error_msg = str(e)
            log_import_attempt(module_path, strategy['name'], False, error_msg)
            failed_modules.append({
                'module_key': module_key,
                'module_path': module_path,
                'error': error_msg
            })
            logger.error(f"Failed to import {module_key} ({module_path}): {error_msg}")
    
    # Check if we have the minimum required modules
    required_modules = ['router', 'factory', 'session', 'tenant']
    has_required = all(key in imported_modules for key in required_modules)
    
    if has_required:
        IMPORTED_MODULES.update(imported_modules)
        return True, imported_modules
    else:
        missing = [key for key in required_modules if key not in imported_modules]
        logger.error(f"Strategy {strategy['name']} failed - missing required modules: {missing}")
        return False, {'failed_modules': failed_modules, 'missing_required': missing}

def validate_imported_modules() -> Dict[str, Any]:
    """Verify all required functions are available"""
    validation_results = {}
    
    try:
        # Validate router module
        if 'router' in IMPORTED_MODULES:
            router_module = IMPORTED_MODULES['router']
            if hasattr(router_module, 'router'):
                validation_results['router'] = 'valid'
            else:
                validation_results['router'] = 'missing_router_attribute'
        else:
            validation_results['router'] = 'module_not_imported'
        
        # Validate factory module
        if 'factory' in IMPORTED_MODULES:
            factory_module = IMPORTED_MODULES['factory']
            if hasattr(factory_module, 'get_agent_factory'):
                validation_results['factory'] = 'valid'
            else:
                validation_results['factory'] = 'missing_get_agent_factory_function'
        else:
            validation_results['factory'] = 'module_not_imported'
        
        # Validate session module
        if 'session' in IMPORTED_MODULES:
            session_module = IMPORTED_MODULES['session']
            if hasattr(session_module, 'get_db'):
                validation_results['session'] = 'valid'
            else:
                validation_results['session'] = 'missing_get_db_function'
        else:
            validation_results['session'] = 'module_not_imported'
        
        # Validate tenant module
        if 'tenant' in IMPORTED_MODULES:
            tenant_module = IMPORTED_MODULES['tenant']
            if hasattr(tenant_module, 'get_current_organization'):
                validation_results['tenant'] = 'valid'
            else:
                validation_results['tenant'] = 'missing_get_current_organization_function'
        else:
            validation_results['tenant'] = 'module_not_imported'
        
        # Validate graph modules
        graph_modules = [
            'coordinator_graph', 'resource_planning_graph', 'financial_graph',
            'stakeholder_graph', 'marketing_graph', 'project_graph',
            'analytics_graph', 'compliance_graph'
        ]
        
        for graph_key in graph_modules:
            if graph_key in IMPORTED_MODULES:
                validation_results[graph_key] = 'available'
            else:
                validation_results[graph_key] = 'not_available'
        
    except Exception as e:
        validation_results['validation_error'] = str(e)
        logger.error(f"Error during module validation: {e}")
    
    return validation_results

def create_diagnostic_report() -> Dict[str, Any]:
    """Generate detailed import status report"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "azure" if os.path.exists('/home/site/wwwroot') else "local",
        "python_path": sys.path[:10],  # First 10 paths for brevity
        "real_agents_available": REAL_AGENTS_AVAILABLE,
        "import_strategy_used": IMPORT_STRATEGY_USED,
        "failed_imports": FAILED_IMPORTS,
        "missing_modules": MISSING_MODULES,
        "imported_modules": list(IMPORTED_MODULES.keys()),
        "module_validation": validate_imported_modules(),
        "azure_paths_exist": {
            "/home/site/wwwroot": os.path.exists('/home/site/wwwroot'),
            "/home/site/wwwroot/app": os.path.exists('/home/site/wwwroot/app'),
            "/home/site/wwwroot/app/agents": os.path.exists('/home/site/wwwroot/app/agents'),
            "/home/site/wwwroot/app/graphs": os.path.exists('/home/site/wwwroot/app/graphs')
        }
    }

def initialize_agents():
    """Initialize agent system with robust import strategy"""
    global REAL_AGENTS_AVAILABLE, IMPORT_STRATEGY_USED, MISSING_MODULES
    
    logger.info("=== Starting Agent Import Process ===")
    
    # Setup Azure Python path
    setup_azure_python_path()
    
    # Try each import strategy
    for strategy in IMPORT_STRATEGIES:
        logger.info(f"Attempting import strategy: {strategy['name']}")
        
        try:
            success, result = try_import_strategy(strategy)
            
            if success:
                logger.info(f"✓ Import strategy '{strategy['name']}' succeeded!")
                REAL_AGENTS_AVAILABLE = True
                IMPORT_STRATEGY_USED = strategy['name']
                
                # Validate the imported modules
                validation_results = validate_imported_modules()
                logger.info(f"Module validation results: {validation_results}")
                
                return True
            else:
                logger.warning(f"✗ Import strategy '{strategy['name']}' failed: {result}")
                
        except Exception as e:
            logger.error(f"✗ Import strategy '{strategy['name']}' crashed: {str(e)}")
            logger.error(traceback.format_exc())
    
    # If we get here, all strategies failed
    logger.error("=== All import strategies failed ===")
    REAL_AGENTS_AVAILABLE = False
    IMPORT_STRATEGY_USED = None
    
    # Collect missing modules
    for strategy in IMPORT_STRATEGIES:
        for module_key, module_path in strategy['paths'].items():
            if module_key not in IMPORTED_MODULES:
                MISSING_MODULES.append(module_path)
    
    MISSING_MODULES = list(set(MISSING_MODULES))  # Remove duplicates
    
    logger.error(f"Missing modules: {MISSING_MODULES}")
    return False

# Initialize FastAPI app
app = FastAPI(title="AI Event Planner - Azure Agents Fixed", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents on startup
@app.on_event("startup")
async def startup_event():
    """Initialize agents on application startup"""
    logger.info("Application starting up...")
    success = initialize_agents()
    
    if success:
        logger.info("✓ Real agents initialized successfully!")
    else:
        logger.warning("✗ Falling back to mock responses")
    
    # Log diagnostic report
    diagnostic_report = create_diagnostic_report()
    logger.info(f"Startup diagnostic report: {diagnostic_report}")

def get_db():
    """Get database session"""
    if REAL_AGENTS_AVAILABLE and 'session' in IMPORTED_MODULES:
        try:
            session_module = IMPORTED_MODULES['session']
            return session_module.get_db()
        except Exception as e:
            logger.error(f"Error getting database session: {e}")
            raise HTTPException(status_code=500, detail="Database connection failed")
    else:
        raise HTTPException(status_code=503, detail="Database session not available")

def get_current_organization(request: Request):
    """Get current organization from request"""
    if REAL_AGENTS_AVAILABLE and 'tenant' in IMPORTED_MODULES:
        try:
            tenant_module = IMPORTED_MODULES['tenant']
            return tenant_module.get_current_organization(request)
        except Exception as e:
            logger.error(f"Error getting current organization: {e}")
            return 1  # Default organization ID
    else:
        return 1  # Default organization ID

def get_agent_factory(db, organization_id: int):
    """Get agent factory instance"""
    if REAL_AGENTS_AVAILABLE and 'factory' in IMPORTED_MODULES:
        try:
            factory_module = IMPORTED_MODULES['factory']
            return factory_module.get_agent_factory(db=db, organization_id=organization_id)
        except Exception as e:
            logger.error(f"Error creating agent factory: {e}")
            raise HTTPException(status_code=500, detail="Agent factory creation failed")
    else:
        raise HTTPException(status_code=503, detail="Agent factory not available")

# Health check endpoint
@app.get("/api/agents/health")
async def health_check():
    """Comprehensive health check for agent systems"""
    
    health_status = {
        "status": "healthy",  # healthy|degraded|unhealthy
        "timestamp": datetime.utcnow().isoformat(),
        "real_agents_available": REAL_AGENTS_AVAILABLE,
        "agent_status": {},
        "import_diagnostics": {
            "strategy_used": IMPORT_STRATEGY_USED,
            "failed_imports": len(FAILED_IMPORTS),
            "missing_modules": len(MISSING_MODULES)
        },
        "database_status": "unknown",
        "environment": "azure" if os.path.exists('/home/site/wwwroot') else "local",
        "python_path": sys.path[:5],  # First 5 paths for brevity
        "version": os.getenv("APP_VERSION", "1.0.0")
    }
    
    # Test each agent type
    agent_types = [
        'coordinator', 'resource_planning', 'financial',
        'stakeholder_management', 'marketing_communications',
        'project_management', 'analytics', 'compliance_security'
    ]
    
    for agent_type in agent_types:
        try:
            if REAL_AGENTS_AVAILABLE:
                # Test actual agent creation
                db = next(get_db())
                factory = get_agent_factory(db=db, organization_id=1)
                agent = factory.create_agent(agent_type, "health_check")
                health_status["agent_status"][agent_type] = "available"
            else:
                health_status["agent_status"][agent_type] = "fallback_mode"
        except Exception as e:
            health_status["agent_status"][agent_type] = f"error: {str(e)}"
    
    # Test database connectivity
    try:
        db = next(get_db())
        # Simple query to test connection
        db.execute("SELECT 1")
        health_status["database_status"] = "connected"
    except Exception as e:
        health_status["database_status"] = f"error: {str(e)}"
    
    # Determine overall status
    failed_agents = sum(1 for status in health_status["agent_status"].values() if status.startswith("error"))
    total_agents = len(health_status["agent_status"])
    
    if failed_agents == 0:
        health_status["status"] = "healthy"
    elif failed_agents < total_agents / 2:
        health_status["status"] = "degraded"
    else:
        health_status["status"] = "unhealthy"
    
    return health_status

# Diagnostic endpoint
@app.get("/api/agents/diagnostics")
async def diagnostics():
    """Detailed diagnostic information for troubleshooting"""
    return create_diagnostic_report()

# Agent chat endpoint
@app.post("/api/agents/chat")
async def agent_chat(
    request: Request,
    db=Depends(get_db),
    organization_id: int = Depends(get_current_organization)
):
    """Handle agent chat requests"""
    try:
        data = await request.json()
        agent_type = data.get("agent_type", "coordinator")
        message = data.get("message", "")
        conversation_id = data.get("conversation_id", "default")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if REAL_AGENTS_AVAILABLE:
            # Use real agents
            try:
                factory = get_agent_factory(db=db, organization_id=organization_id)
                agent = factory.create_agent(agent_type, conversation_id)
                
                # Process message with real agent
                response = agent.process_message(message)
                
                return {
                    "response": response,
                    "conversation_id": conversation_id,
                    "agent_type": agent_type,
                    "organization_id": organization_id,
                    "using_real_agent": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Real agent processing failed: {e}")
                # Fall back to mock response
                return get_fallback_response(agent_type, message, conversation_id)
        else:
            # Use fallback system
            return get_fallback_response(agent_type, message, conversation_id)
            
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_fallback_response(agent_type: str, message: str, conversation_id: str) -> Dict[str, Any]:
    """Generate intelligent fallback response"""
    
    fallback_responses = {
        'coordinator': """I'm the Event Coordinator, but I'm currently running in limited mode. 
        I can still help you with basic event planning questions, but my full AI capabilities are temporarily unavailable. 
        
        For immediate assistance, please:
        1. Check our event planning templates
        2. Review our planning checklist
        3. Contact our support team for urgent matters
        
        What specific aspect of event planning can I help you with today?""",
        
        'resource_planning': """I'm the Resource Planning agent, currently in limited mode. 
        
        For resource planning, I recommend:
        1. Review our standard resource templates
        2. Check our vendor directory
        3. Use our resource calculator tools
        
        What type of resources are you planning for your event?""",
        
        'financial': """I'm the Financial Planning agent, currently in limited mode.
        
        For budget planning, please:
        1. Use our budget templates
        2. Check our cost estimation guides
        3. Review vendor pricing information
        
        What's your estimated budget range for this event?""",
        
        'stakeholder_management': """I'm the Stakeholder Management agent, currently in limited mode.
        
        For stakeholder management:
        1. Use our stakeholder mapping templates
        2. Check our communication templates
        3. Review our engagement strategies
        
        Who are the key stakeholders for your event?""",
        
        'marketing_communications': """I'm the Marketing Communications agent, currently in limited mode.
        
        For marketing your event:
        1. Use our marketing templates
        2. Check our social media guides
        3. Review our promotional strategies
        
        What's your target audience for this event?""",
        
        'project_management': """I'm the Project Management agent, currently in limited mode.
        
        For project management:
        1. Use our project timeline templates
        2. Check our task management guides
        3. Review our milestone tracking tools
        
        What's the timeline for your event?""",
        
        'analytics': """I'm the Analytics agent, currently in limited mode.
        
        For event analytics:
        1. Use our metrics tracking templates
        2. Check our reporting guides
        3. Review our KPI frameworks
        
        What metrics are most important for your event?""",
        
        'compliance_security': """I'm the Compliance & Security agent, currently in limited mode.
        
        For compliance and security:
        1. Review our compliance checklists
        2. Check our security guidelines
        3. Consult our legal requirements guide
        
        What type of event are you planning and what compliance requirements do you need to meet?"""
    }
    
    response_text = fallback_responses.get(
        agent_type, 
        f"I apologize, but the {agent_type} agent is currently unavailable. Please try again later or contact support."
    )
    
    return {
        "response": response_text,
        "conversation_id": conversation_id,
        "agent_type": agent_type,
        "organization_id": None,
        "using_real_agent": False,
        "fallback_reason": "agent_unavailable",
        "timestamp": datetime.utcnow().isoformat()
    }

# Include agent router if available
if REAL_AGENTS_AVAILABLE and 'router' in IMPORTED_MODULES:
    try:
        router_module = IMPORTED_MODULES['router']
        if hasattr(router_module, 'router'):
            app.include_router(router_module.router, prefix="/api/agents", tags=["agents"])
            logger.info("✓ Agent router included successfully")
    except Exception as e:
        logger.error(f"Failed to include agent router: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "AI Event Planner - Azure Agents Fixed",
        "real_agents_available": REAL_AGENTS_AVAILABLE,
        "import_strategy_used": IMPORT_STRATEGY_USED,
        "environment": "azure" if os.path.exists('/home/site/wwwroot') else "local",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    # Run the application
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
