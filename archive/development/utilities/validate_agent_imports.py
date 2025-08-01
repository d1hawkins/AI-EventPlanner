#!/usr/bin/env python3
"""
Standalone validator for agent imports in Azure environment.
Run this script during deployment to ensure everything works.
"""

import sys
import os
import importlib
import traceback
from typing import Dict, List, Any
from datetime import datetime

def validate_core_imports() -> Dict[str, Any]:
    """Validate core module imports"""
    print("\n=== Validating Core Imports ===")
    results = {}
    
    core_modules = [
        'app.agents.api_router',
        'app.agents.agent_factory',
        'app.db.session',
        'app.middleware.tenant'
    ]
    
    for module in core_modules:
        try:
            imported_module = importlib.import_module(module)
            results[module] = {
                "status": "success",
                "file": getattr(imported_module, '__file__', 'unknown'),
                "attributes": dir(imported_module)[:10]  # First 10 attributes
            }
            print(f"  ✓ {module}")
        except Exception as e:
            results[module] = {
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"  ✗ {module}: {str(e)}")
    
    return results

def validate_graph_imports() -> Dict[str, Any]:
    """Validate graph module imports"""
    print("\n=== Validating Graph Imports ===")
    results = {}
    
    graph_modules = [
        'app.graphs.coordinator_graph',
        'app.graphs.resource_planning_graph',
        'app.graphs.financial_graph',
        'app.graphs.stakeholder_management_graph',
        'app.graphs.marketing_communications_graph',
        'app.graphs.project_management_graph',
        'app.graphs.analytics_graph',
        'app.graphs.compliance_security_graph'
    ]
    
    for module in graph_modules:
        try:
            imported_module = importlib.import_module(module)
            results[module] = {
                "status": "success",
                "file": getattr(imported_module, '__file__', 'unknown'),
                "attributes": dir(imported_module)[:10]  # First 10 attributes
            }
            print(f"  ✓ {module}")
        except Exception as e:
            results[module] = {
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"  ✗ {module}: {str(e)}")
    
    return results

def validate_agent_creation() -> Dict[str, Any]:
    """Test actual agent creation"""
    print("\n=== Validating Agent Creation ===")
    results = {}
    
    try:
        # Try to import required modules
        from app.agents.agent_factory import get_agent_factory
        from app.db.session import get_db
        
        print("  ✓ Successfully imported agent factory and database session")
        
        # Mock database session for testing
        try:
            db = next(get_db())
            print("  ✓ Database session created successfully")
            
            factory = get_agent_factory(db=db, organization_id=1)
            print("  ✓ Agent factory created successfully")
            
            agent_types = [
                'coordinator',
                'resource_planning',
                'financial',
                'stakeholder_management',
                'marketing_communications',
                'project_management',
                'analytics',
                'compliance_security'
            ]
            
            for agent_type in agent_types:
                try:
                    agent = factory.create_agent(agent_type, "test_conversation")
                    results[agent_type] = {
                        "status": "success",
                        "agent_type": str(type(agent)),
                        "methods": [method for method in dir(agent) if not method.startswith('_')][:10]
                    }
                    print(f"  ✓ {agent_type} agent created successfully")
                except Exception as e:
                    results[agent_type] = {
                        "status": "failed",
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
                    print(f"  ✗ {agent_type} agent creation failed: {str(e)}")
                    
        except Exception as e:
            results["database_session"] = {
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"  ✗ Database session creation failed: {str(e)}")
            
    except Exception as e:
        results["agent_factory"] = {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(f"  ✗ Agent factory import failed: {str(e)}")
    
    return results

def validate_dependencies() -> Dict[str, Any]:
    """Validate required dependencies"""
    print("\n=== Validating Dependencies ===")
    results = {}
    
    dependencies = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'pydantic',
        'langchain',
        'langgraph',
        'openai',
        'google.generativeai'
    ]
    
    for dep in dependencies:
        try:
            module = importlib.import_module(dep)
            version = getattr(module, '__version__', 'unknown')
            results[dep] = {
                "status": "available",
                "version": version,
                "file": getattr(module, '__file__', 'unknown')
            }
            print(f"  ✓ {dep} ({version})")
        except Exception as e:
            results[dep] = {
                "status": "missing",
                "error": str(e)
            }
            print(f"  ✗ {dep}: {str(e)}")
    
    return results

def validate_environment() -> Dict[str, Any]:
    """Validate environment setup"""
    print("\n=== Validating Environment ===")
    
    environment = "azure" if os.path.exists('/home/site/wwwroot') else "local"
    print(f"  Environment: {environment}")
    
    # Check Python path
    print(f"  Python version: {sys.version}")
    print(f"  Working directory: {os.getcwd()}")
    print(f"  Python path entries: {len(sys.path)}")
    
    # Check Azure-specific paths
    azure_paths = [
        '/home/site/wwwroot',
        '/home/site/wwwroot/app',
        '/home/site/wwwroot/app/agents',
        '/home/site/wwwroot/app/graphs'
    ]
    
    path_status = {}
    for path in azure_paths:
        exists = os.path.exists(path)
        path_status[path] = exists
        status = "✓" if exists else "✗"
        print(f"  {status} {path}")
    
    # Check local paths
    local_paths = [
        'app',
        'app/agents',
        'app/graphs',
        'app/db',
        'app/middleware'
    ]
    
    for path in local_paths:
        exists = os.path.exists(path)
        path_status[path] = exists
        status = "✓" if exists else "✗"
        print(f"  {status} {path}")
    
    return {
        "environment": environment,
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "python_path_count": len(sys.path),
        "path_status": path_status
    }

def validate_specific_functions() -> Dict[str, Any]:
    """Validate specific required functions exist"""
    print("\n=== Validating Specific Functions ===")
    results = {}
    
    function_tests = [
        {
            "module": "app.agents.api_router",
            "attribute": "router",
            "description": "FastAPI router"
        },
        {
            "module": "app.agents.agent_factory",
            "attribute": "get_agent_factory",
            "description": "Agent factory function"
        },
        {
            "module": "app.db.session",
            "attribute": "get_db",
            "description": "Database session function"
        },
        {
            "module": "app.middleware.tenant",
            "attribute": "get_current_organization",
            "description": "Tenant middleware function"
        }
    ]
    
    for test in function_tests:
        try:
            module = importlib.import_module(test["module"])
            if hasattr(module, test["attribute"]):
                attr = getattr(module, test["attribute"])
                results[f"{test['module']}.{test['attribute']}"] = {
                    "status": "available",
                    "type": str(type(attr)),
                    "description": test["description"]
                }
                print(f"  ✓ {test['module']}.{test['attribute']} ({test['description']})")
            else:
                results[f"{test['module']}.{test['attribute']}"] = {
                    "status": "missing_attribute",
                    "available_attributes": dir(module)[:10],
                    "description": test["description"]
                }
                print(f"  ✗ {test['module']}.{test['attribute']} - attribute missing")
        except Exception as e:
            results[f"{test['module']}.{test['attribute']}"] = {
                "status": "import_failed",
                "error": str(e),
                "description": test["description"]
            }
            print(f"  ✗ {test['module']}.{test['attribute']} - import failed: {str(e)}")
    
    return results

def generate_validation_report(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive validation report"""
    
    # Count successes and failures
    core_results = results.get("core_imports", {})
    graph_results = results.get("graph_imports", {})
    agent_results = results.get("agent_creation", {})
    dependency_results = results.get("dependencies", {})
    function_results = results.get("function_validation", {})
    
    core_success = sum(1 for r in core_results.values() if r.get("status") == "success")
    graph_success = sum(1 for r in graph_results.values() if r.get("status") == "success")
    agent_success = sum(1 for r in agent_results.values() if r.get("status") == "success")
    dep_success = sum(1 for r in dependency_results.values() if r.get("status") == "available")
    func_success = sum(1 for r in function_results.values() if r.get("status") == "available")
    
    total_core = len(core_results)
    total_graph = len(graph_results)
    total_agent = len(agent_results)
    total_dep = len(dependency_results)
    total_func = len(function_results)
    
    # Determine overall status
    critical_success = core_success + func_success
    critical_total = total_core + total_func
    
    if critical_success == critical_total:
        overall_status = "healthy"
    elif critical_success >= critical_total * 0.75:
        overall_status = "degraded"
    else:
        overall_status = "critical"
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": overall_status,
        "summary": {
            "core_imports": f"{core_success}/{total_core}",
            "graph_imports": f"{graph_success}/{total_graph}",
            "agent_creation": f"{agent_success}/{total_agent}",
            "dependencies": f"{dep_success}/{total_dep}",
            "function_validation": f"{func_success}/{total_func}"
        },
        "detailed_results": results,
        "recommendations": []
    }
    
    # Add recommendations based on results
    if core_success < total_core:
        report["recommendations"].append("Fix core module import issues")
    
    if graph_success < total_graph:
        report["recommendations"].append("Address graph module import problems")
    
    if agent_success < total_agent:
        report["recommendations"].append("Resolve agent creation failures")
    
    if dep_success < total_dep:
        report["recommendations"].append("Install missing dependencies")
    
    if func_success < total_func:
        report["recommendations"].append("Ensure required functions are available")
    
    return report

def print_summary(report: Dict[str, Any]):
    """Print validation summary"""
    print("\n" + "="*60)
    print("AGENT IMPORT VALIDATION SUMMARY")
    print("="*60)
    
    print(f"Timestamp: {report['timestamp']}")
    print(f"Overall Status: {report['overall_status'].upper()}")
    
    print(f"\nResults Summary:")
    for category, result in report['summary'].items():
        print(f"  {category.replace('_', ' ').title()}: {result}")
    
    if report['recommendations']:
        print(f"\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "="*60)

def main():
    """Main validation function"""
    print("Starting Agent Import Validation...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Run all validations
    results = {}
    
    results["environment"] = validate_environment()
    results["dependencies"] = validate_dependencies()
    results["core_imports"] = validate_core_imports()
    results["graph_imports"] = validate_graph_imports()
    results["function_validation"] = validate_specific_functions()
    results["agent_creation"] = validate_agent_creation()
    
    # Generate report
    report = generate_validation_report(results)
    
    # Print summary
    print_summary(report)
    
    # Save detailed report
    try:
        import json
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_validation_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {filename}")
    except Exception as e:
        print(f"\nWarning: Could not save detailed report: {e}")
    
    # Return exit code based on status
    status = report['overall_status']
    if status == "healthy":
        print("\n✓ All critical validations passed! Agents should work correctly.")
        return 0
    elif status == "degraded":
        print("\n⚠ Some issues detected, but core functionality should work.")
        return 1
    else:
        print("\n✗ Critical issues detected. Agents may not function properly.")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
