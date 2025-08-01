#!/usr/bin/env python3
"""
Azure Import Diagnostic System
Comprehensive diagnostic system to identify and troubleshoot import issues.
"""

import os
import sys
import importlib
import logging
import traceback
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureImportDiagnostics:
    """Comprehensive diagnostic system for Azure agent imports"""
    
    def __init__(self):
        self.environment = "azure" if os.path.exists('/home/site/wwwroot') else "local"
        self.python_path = sys.path.copy()
        self.import_results = {}
        self.missing_modules = []
        self.graph_modules = {}
        self.database_status = "unknown"
        self.recommendations = []
        
    def diagnose_import_environment(self) -> Dict[str, Any]:
        """Comprehensive import environment diagnosis"""
        logger.info("=== Starting Import Environment Diagnosis ===")
        
        # Basic environment info
        env_info = {
            "environment": self.environment,
            "python_version": sys.version,
            "python_path": self.python_path[:15],  # First 15 paths
            "working_directory": os.getcwd(),
            "azure_paths_exist": self._check_azure_paths(),
            "file_structure": self._analyze_file_structure()
        }
        
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        return env_info
    
    def _check_azure_paths(self) -> Dict[str, bool]:
        """Check if Azure-specific paths exist"""
        azure_paths = {
            "/home/site/wwwroot": os.path.exists('/home/site/wwwroot'),
            "/home/site/wwwroot/app": os.path.exists('/home/site/wwwroot/app'),
            "/home/site/wwwroot/app/agents": os.path.exists('/home/site/wwwroot/app/agents'),
            "/home/site/wwwroot/app/graphs": os.path.exists('/home/site/wwwroot/app/graphs'),
            "/home/site/wwwroot/app/tools": os.path.exists('/home/site/wwwroot/app/tools'),
            "/home/site/wwwroot/app/utils": os.path.exists('/home/site/wwwroot/app/utils'),
            "/home/site/wwwroot/app/db": os.path.exists('/home/site/wwwroot/app/db'),
            "/home/site/wwwroot/app/middleware": os.path.exists('/home/site/wwwroot/app/middleware')
        }
        
        for path, exists in azure_paths.items():
            if exists:
                logger.info(f"✓ Path exists: {path}")
            else:
                logger.warning(f"✗ Path missing: {path}")
        
        return azure_paths
    
    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze the current file structure"""
        structure = {}
        
        # Check local app structure
        if os.path.exists('app'):
            structure['local_app'] = self._list_directory_contents('app')
        
        # Check Azure app structure
        if os.path.exists('/home/site/wwwroot/app'):
            structure['azure_app'] = self._list_directory_contents('/home/site/wwwroot/app')
        
        return structure
    
    def _list_directory_contents(self, path: str) -> Dict[str, List[str]]:
        """List contents of a directory"""
        contents = {}
        
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    try:
                        contents[item] = os.listdir(item_path)
                    except PermissionError:
                        contents[item] = ["Permission denied"]
                    except Exception as e:
                        contents[item] = [f"Error: {str(e)}"]
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            contents = {"error": str(e)}
        
        return contents
    
    def test_module_imports(self) -> Dict[str, Any]:
        """Test each required module import individually"""
        logger.info("=== Testing Module Imports ===")
        
        # Core modules to test
        core_modules = {
            'router': [
                'app.agents.api_router',
                'agents.api_router',
                'site.wwwroot.app.agents.api_router'
            ],
            'factory': [
                'app.agents.agent_factory',
                'agents.agent_factory',
                'site.wwwroot.app.agents.agent_factory'
            ],
            'session': [
                'app.db.session',
                'db.session',
                'site.wwwroot.app.db.session'
            ],
            'tenant': [
                'app.middleware.tenant',
                'middleware.tenant',
                'site.wwwroot.app.middleware.tenant'
            ]
        }
        
        results = {}
        
        for module_key, module_paths in core_modules.items():
            results[module_key] = {}
            success = False
            
            for module_path in module_paths:
                try:
                    module = importlib.import_module(module_path)
                    results[module_key][module_path] = {
                        "status": "success",
                        "module": str(module),
                        "file": getattr(module, '__file__', 'unknown')
                    }
                    logger.info(f"✓ Successfully imported {module_key}: {module_path}")
                    success = True
                    break  # Stop trying other paths if one succeeds
                except Exception as e:
                    results[module_key][module_path] = {
                        "status": "failed",
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
                    logger.error(f"✗ Failed to import {module_key} ({module_path}): {e}")
            
            if not success:
                self.missing_modules.append(module_key)
                self.recommendations.append(f"Fix import issues for {module_key} module")
        
        self.import_results = results
        return results
    
    def validate_agent_dependencies(self) -> Dict[str, Any]:
        """Check if all agent dependencies are available"""
        logger.info("=== Validating Agent Dependencies ===")
        
        dependencies = {
            'fastapi': 'FastAPI web framework',
            'uvicorn': 'ASGI server',
            'sqlalchemy': 'Database ORM',
            'psycopg2': 'PostgreSQL adapter',
            'pydantic': 'Data validation',
            'langchain': 'LangChain framework',
            'langgraph': 'LangGraph for agent workflows',
            'openai': 'OpenAI API client',
            'google.generativeai': 'Google AI client'
        }
        
        results = {}
        missing_deps = []
        
        for dep_name, description in dependencies.items():
            try:
                module = importlib.import_module(dep_name)
                version = getattr(module, '__version__', 'unknown')
                results[dep_name] = {
                    "status": "available",
                    "version": version,
                    "description": description,
                    "file": getattr(module, '__file__', 'unknown')
                }
                logger.info(f"✓ {dep_name} ({version}): {description}")
            except Exception as e:
                results[dep_name] = {
                    "status": "missing",
                    "error": str(e),
                    "description": description
                }
                missing_deps.append(dep_name)
                logger.error(f"✗ Missing dependency: {dep_name} - {e}")
        
        if missing_deps:
            self.recommendations.append(f"Install missing dependencies: {', '.join(missing_deps)}")
        
        return results
    
    def test_graph_imports(self) -> Dict[str, Any]:
        """Test all graph module imports"""
        logger.info("=== Testing Graph Module Imports ===")
        
        graph_modules = {
            'coordinator_graph': [
                'app.graphs.coordinator_graph',
                'graphs.coordinator_graph',
                'site.wwwroot.app.graphs.coordinator_graph'
            ],
            'resource_planning_graph': [
                'app.graphs.resource_planning_graph',
                'graphs.resource_planning_graph',
                'site.wwwroot.app.graphs.resource_planning_graph'
            ],
            'financial_graph': [
                'app.graphs.financial_graph',
                'graphs.financial_graph',
                'site.wwwroot.app.graphs.financial_graph'
            ],
            'stakeholder_graph': [
                'app.graphs.stakeholder_management_graph',
                'graphs.stakeholder_management_graph',
                'site.wwwroot.app.graphs.stakeholder_management_graph'
            ],
            'marketing_graph': [
                'app.graphs.marketing_communications_graph',
                'graphs.marketing_communications_graph',
                'site.wwwroot.app.graphs.marketing_communications_graph'
            ],
            'project_graph': [
                'app.graphs.project_management_graph',
                'graphs.project_management_graph',
                'site.wwwroot.app.graphs.project_management_graph'
            ],
            'analytics_graph': [
                'app.graphs.analytics_graph',
                'graphs.analytics_graph',
                'site.wwwroot.app.graphs.analytics_graph'
            ],
            'compliance_graph': [
                'app.graphs.compliance_security_graph',
                'graphs.compliance_security_graph',
                'site.wwwroot.app.graphs.compliance_security_graph'
            ]
        }
        
        results = {}
        
        for graph_key, module_paths in graph_modules.items():
            results[graph_key] = {}
            success = False
            
            for module_path in module_paths:
                try:
                    module = importlib.import_module(module_path)
                    results[graph_key][module_path] = {
                        "status": "available",
                        "module": str(module),
                        "file": getattr(module, '__file__', 'unknown')
                    }
                    logger.info(f"✓ Graph available: {graph_key} ({module_path})")
                    success = True
                    break
                except Exception as e:
                    results[graph_key][module_path] = {
                        "status": "missing",
                        "error": str(e)
                    }
                    logger.error(f"✗ Graph missing: {graph_key} ({module_path}) - {e}")
            
            if success:
                self.graph_modules[graph_key] = "available"
            else:
                self.graph_modules[graph_key] = "missing"
        
        return results
    
    def validate_database_connectivity(self) -> Dict[str, Any]:
        """Test database session creation"""
        logger.info("=== Testing Database Connectivity ===")
        
        db_result = {
            "status": "unknown",
            "error": None,
            "connection_string": "hidden",
            "environment_vars": {}
        }
        
        # Check environment variables
        db_env_vars = [
            'DATABASE_URL', 'AZURE_DATABASE_URL', 'POSTGRES_URL',
            'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'
        ]
        
        for var in db_env_vars:
            value = os.getenv(var)
            if value:
                # Hide sensitive information
                if 'password' in var.lower() or 'url' in var.lower():
                    db_result["environment_vars"][var] = "***hidden***"
                else:
                    db_result["environment_vars"][var] = value
            else:
                db_result["environment_vars"][var] = None
        
        # Try to import and test database session
        try:
            # Try different import paths for session module
            session_module = None
            for module_path in ['app.db.session', 'db.session']:
                try:
                    session_module = importlib.import_module(module_path)
                    break
                except ImportError:
                    continue
            
            if session_module and hasattr(session_module, 'get_db'):
                try:
                    db = next(session_module.get_db())
                    # Try a simple query with proper SQLAlchemy text
                    from sqlalchemy import text
                    db.execute(text("SELECT 1"))
                    db_result["status"] = "connected"
                    logger.info("✓ Database connection successful")
                except Exception as e:
                    db_result["status"] = "connection_failed"
                    db_result["error"] = str(e)
                    logger.error(f"✗ Database connection failed: {e}")
            else:
                db_result["status"] = "session_module_not_available"
                db_result["error"] = "Could not import database session module"
                logger.error("✗ Database session module not available")
                
        except Exception as e:
            db_result["status"] = "error"
            db_result["error"] = str(e)
            logger.error(f"✗ Database validation error: {e}")
        
        self.database_status = db_result["status"]
        
        if db_result["status"] != "connected":
            self.recommendations.append("Fix database connectivity issues")
        
        return db_result
    
    def generate_import_report(self) -> Dict[str, Any]:
        """Create detailed report of import status"""
        logger.info("=== Generating Import Report ===")
        
        # Run all diagnostics
        env_info = self.diagnose_import_environment()
        import_results = self.test_module_imports()
        dependency_results = self.validate_agent_dependencies()
        graph_results = self.test_graph_imports()
        db_results = self.validate_database_connectivity()
        
        # Generate summary
        total_core_modules = len(import_results)
        successful_core_modules = sum(1 for module_data in import_results.values() 
                                    if any(result["status"] == "success" for result in module_data.values()))
        
        total_graph_modules = len(self.graph_modules)
        available_graph_modules = sum(1 for status in self.graph_modules.values() if status == "available")
        
        # Create comprehensive report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment_info": env_info,
            "import_summary": {
                "core_modules": {
                    "total": total_core_modules,
                    "successful": successful_core_modules,
                    "failed": total_core_modules - successful_core_modules
                },
                "graph_modules": {
                    "total": total_graph_modules,
                    "available": available_graph_modules,
                    "missing": total_graph_modules - available_graph_modules
                }
            },
            "detailed_results": {
                "core_imports": import_results,
                "dependencies": dependency_results,
                "graph_imports": graph_results,
                "database": db_results
            },
            "missing_modules": self.missing_modules,
            "recommendations": self.recommendations,
            "overall_status": self._determine_overall_status(successful_core_modules, total_core_modules)
        }
        
        return report
    
    def _determine_overall_status(self, successful: int, total: int) -> str:
        """Determine overall import status"""
        if successful == total:
            return "healthy"
        elif successful >= total * 0.75:
            return "degraded"
        else:
            return "critical"
    
    def save_report_to_file(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save diagnostic report to file"""
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"azure_import_diagnostics_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Diagnostic report saved to: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save report to {filename}: {e}")
            return None
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a human-readable summary of the diagnostic report"""
        print("\n" + "="*60)
        print("AZURE IMPORT DIAGNOSTICS SUMMARY")
        print("="*60)
        
        print(f"Environment: {report['environment_info']['environment']}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Overall Status: {report['overall_status'].upper()}")
        
        print(f"\nCore Modules: {report['import_summary']['core_modules']['successful']}/{report['import_summary']['core_modules']['total']} successful")
        print(f"Graph Modules: {report['import_summary']['graph_modules']['available']}/{report['import_summary']['graph_modules']['total']} available")
        print(f"Database Status: {report['detailed_results']['database']['status']}")
        
        if report['missing_modules']:
            print(f"\nMissing Modules: {', '.join(report['missing_modules'])}")
        
        if report['recommendations']:
            print("\nRecommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)

def main():
    """Main diagnostic function"""
    print("Starting Azure Import Diagnostics...")
    
    diagnostics = AzureImportDiagnostics()
    report = diagnostics.generate_import_report()
    
    # Print summary
    diagnostics.print_summary(report)
    
    # Save detailed report
    filename = diagnostics.save_report_to_file(report)
    if filename:
        print(f"\nDetailed report saved to: {filename}")
    
    # Return exit code based on status
    status = report['overall_status']
    if status == "healthy":
        print("\n✓ All systems operational!")
        return 0
    elif status == "degraded":
        print("\n⚠ Some issues detected, but system should work with limitations.")
        return 1
    else:
        print("\n✗ Critical issues detected. System may not function properly.")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
