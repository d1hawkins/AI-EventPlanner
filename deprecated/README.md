# Deprecated Azure Deployment Scripts

This folder contains outdated and incomplete Azure deployment scripts that have been moved here to clean up the project structure.

## ⚠️ **DO NOT USE THESE SCRIPTS**

These scripts are kept for historical reference only and should not be used for deployment.

## 📁 **Contents**

### **Outdated Deployment Scripts**
- `azure-deploy.sh` - Basic deployment without agent support
- `azure-deploy-comprehensive.sh` - Early comprehensive attempt
- `azure-deploy-fixed.sh` - Various fix attempts
- `azure-deploy-docker.sh*` - Docker-based deployments (complex)
- `azure-deploy-saas*.sh` - Multiple SaaS deployment iterations
- `azure-deploy-simple*.sh` - Simplified deployment attempts
- `azure-deploy-static.sh` - Static site deployment
- `azure-deploy-html*.sh` - HTML-only deployments
- `azure-deploy-typeddict-fix.sh` - TypedDict specific fix

### **Outdated Support Scripts**
- `deploy-to-azure*.sh` - Various deployment helpers
- `deploy-simple.sh` - Simple deployment script
- `deploy-app-to-azure.sh` - App deployment script
- `verify-*.sh` - Verification scripts
- `test_azure_fix.sh` - Testing scripts
- `check_azure_logs.sh` - Log checking scripts
- `update-azure-agents.sh` - Agent update scripts

### **Outdated Docker Files**
- `Dockerfile.saas.fixed*` - Fixed Dockerfile versions
- `apply_docker_security_fixes*.sh` - Docker security scripts
- `.github/workflows/azure-deploy-docker.yml.fixed` - GitHub Actions

### **Outdated Environment Files**
- `.env.azure.fixed` - Fixed environment file
- `.env.azure2` - Alternative environment file
- `app_simplified.py` - Simplified app version
- `requirements_simplified.txt` - Simplified requirements

## ✅ **Use These Instead**

For current Azure deployment, use these scripts from the root directory:

### **Primary Scripts (RECOMMENDED)**
- `azure-deploy-saas-complete.sh` - Complete SaaS deployment with agents
- `setup-azure-logging-comprehensive.sh` - Comprehensive monitoring
- `fix-azure-timeout-now.sh` - Fix timeout issues
- `quick-fix-agents.sh` - Install agent dependencies
- `final-agent-fix.sh` - Final agent activation

### **Current Working Files**
- `Dockerfile.saas` - Current SaaS Dockerfile
- `.env.azure` - Current environment file
- `app_adapter_with_agents_fixed.py` - Current app adapter
- `requirements_with_agents.txt` - Current requirements

## 📈 **Migration History**

These scripts represent the evolution of the Azure deployment process:

1. **Early Attempts** - Basic deployment scripts
2. **Docker Phase** - Attempted containerization
3. **SaaS Integration** - Adding SaaS functionality
4. **Agent Integration** - Adding AI agent support
5. **Current Solution** - Working deployment with agents

## 🗑️ **Cleanup Date**

Moved to deprecated folder: June 14, 2025

---

**Note**: If you need to reference any of these scripts for historical purposes, they are preserved here. However, for any new deployments, always use the current scripts from the root directory.
