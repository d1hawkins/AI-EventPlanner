#!/bin/bash
set -e

echo "=== Azure Agent Deployment Fix ==="
echo "Timestamp: $(date)"
echo "Environment: Azure App Service"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create directory if it doesn't exist
ensure_directory() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        log "Creating directory: $dir"
        mkdir -p "$dir" || {
            log "ERROR: Failed to create directory $dir"
            return 1
        }
    else
        log "Directory exists: $dir"
    fi
}

# Function to copy files with error handling
safe_copy() {
    local src="$1"
    local dest="$2"
    local desc="$3"
    
    if [ -e "$src" ]; then
        log "Copying $desc: $src -> $dest"
        cp -r "$src" "$dest" || {
            log "WARNING: Failed to copy $desc from $src to $dest"
            return 1
        }
        log "Successfully copied $desc"
    else
        log "WARNING: Source not found for $desc: $src"
        return 1
    fi
}

# Function to set file permissions
set_permissions() {
    local path="$1"
    local perms="$2"
    
    if [ -e "$path" ]; then
        log "Setting permissions $perms on $path"
        chmod -R "$perms" "$path" || {
            log "WARNING: Failed to set permissions on $path"
            return 1
        }
    else
        log "WARNING: Path not found for permission setting: $path"
        return 1
    fi
}

# Main deployment function
main() {
    log "Starting Azure Agent Deployment Fix"
    
    # Check if we're in Azure environment
    if [ -d "/home/site/wwwroot" ]; then
        log "Detected Azure App Service environment"
        AZURE_ROOT="/home/site/wwwroot"
    else
        log "Local environment detected - using current directory"
        AZURE_ROOT="."
    fi
    
    # Ensure all required directories exist
    log "Creating required directory structure..."
    
    directories=(
        "$AZURE_ROOT/app"
        "$AZURE_ROOT/app/agents"
        "$AZURE_ROOT/app/graphs"
        "$AZURE_ROOT/app/tools"
        "$AZURE_ROOT/app/utils"
        "$AZURE_ROOT/app/db"
        "$AZURE_ROOT/app/middleware"
        "$AZURE_ROOT/app/schemas"
        "$AZURE_ROOT/app/auth"
        "$AZURE_ROOT/app/subscription"
        "$AZURE_ROOT/app/state"
        "$AZURE_ROOT/app/web"
        "$AZURE_ROOT/migrations"
        "$AZURE_ROOT/scripts"
    )
    
    for dir in "${directories[@]}"; do
        ensure_directory "$dir"
    done
    
    # Copy core application files
    log "Copying core application files..."
    
    # Copy agent modules
    if [ -d "app/agents" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping agent modules copy (files already in place)"
        else
            log "Copying agent modules directory..."
            cp -r "app/agents/." "$AZURE_ROOT/app/agents/" || {
                log "WARNING: Failed to copy agent modules directory"
            }
        fi
        
        # Ensure specific agent files exist
        agent_files=(
            "app/agents/__init__.py"
            "app/agents/api_router.py"
            "app/agents/agent_factory.py"
        )
        
        for file in "${agent_files[@]}"; do
            if [ -f "$file" ]; then
                if [ "$AZURE_ROOT" = "." ]; then
                    log "✓ Agent file present: $(basename $file)"
                else
                    safe_copy "$file" "$AZURE_ROOT/$file" "agent file $(basename $file)"
                fi
            else
                log "WARNING: Missing agent file: $file"
            fi
        done
    else
        log "ERROR: app/agents directory not found!"
        return 1
    fi
    
    # Copy graph modules
    if [ -d "app/graphs" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping graph modules copy (files already in place)"
        else
            log "Copying graph modules directory..."
            cp -r "app/graphs/." "$AZURE_ROOT/app/graphs/" || {
                log "WARNING: Failed to copy graph modules directory"
            }
        fi
        
        # Ensure specific graph files exist
        graph_files=(
            "app/graphs/__init__.py"
            "app/graphs/coordinator_graph.py"
            "app/graphs/resource_planning_graph.py"
            "app/graphs/financial_graph.py"
            "app/graphs/stakeholder_management_graph.py"
            "app/graphs/marketing_communications_graph.py"
            "app/graphs/project_management_graph.py"
            "app/graphs/analytics_graph.py"
            "app/graphs/compliance_security_graph.py"
        )
        
        for file in "${graph_files[@]}"; do
            if [ -f "$file" ]; then
                if [ "$AZURE_ROOT" = "." ]; then
                    log "✓ Graph file present: $(basename $file)"
                else
                    safe_copy "$file" "$AZURE_ROOT/$file" "graph file $(basename $file)"
                fi
            else
                log "WARNING: Missing graph file: $file"
            fi
        done
    else
        log "ERROR: app/graphs directory not found!"
        return 1
    fi
    
    # Copy tools modules
    if [ -d "app/tools" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping tools modules copy (files already in place)"
        else
            log "Copying tools modules directory..."
            cp -r "app/tools/." "$AZURE_ROOT/app/tools/" || {
                log "WARNING: Failed to copy tools modules directory"
            }
        fi
    else
        log "WARNING: app/tools directory not found"
    fi
    
    # Copy utils modules
    if [ -d "app/utils" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping utils modules copy (files already in place)"
        else
            log "Copying utils modules directory..."
            cp -r "app/utils/." "$AZURE_ROOT/app/utils/" || {
                log "WARNING: Failed to copy utils modules directory"
            }
        fi
        
        # Ensure specific utility files exist
        util_files=(
            "app/utils/__init__.py"
            "app/utils/llm_factory.py"
            "app/utils/logging_utils.py"
        )
        
        for file in "${util_files[@]}"; do
            if [ -f "$file" ]; then
                if [ "$AZURE_ROOT" = "." ]; then
                    log "✓ Utility file present: $(basename $file)"
                else
                    safe_copy "$file" "$AZURE_ROOT/$file" "utility file $(basename $file)"
                fi
            else
                log "WARNING: Missing utility file: $file"
            fi
        done
    else
        log "ERROR: app/utils directory not found!"
        return 1
    fi
    
    # Copy database modules
    if [ -d "app/db" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping database modules copy (files already in place)"
        else
            log "Copying database modules directory..."
            cp -r "app/db/." "$AZURE_ROOT/app/db/" || {
                log "WARNING: Failed to copy database modules directory"
            }
        fi
        
        # Ensure specific database files exist
        db_files=(
            "app/db/__init__.py"
            "app/db/session.py"
            "app/db/models.py"
            "app/db/base.py"
        )
        
        for file in "${db_files[@]}"; do
            if [ -f "$file" ]; then
                if [ "$AZURE_ROOT" = "." ]; then
                    log "✓ Database file present: $(basename $file)"
                else
                    safe_copy "$file" "$AZURE_ROOT/$file" "database file $(basename $file)"
                fi
            else
                log "WARNING: Missing database file: $file"
            fi
        done
    else
        log "ERROR: app/db directory not found!"
        return 1
    fi
    
    # Copy middleware modules
    if [ -d "app/middleware" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping middleware modules copy (files already in place)"
        else
            log "Copying middleware modules directory..."
            cp -r "app/middleware/." "$AZURE_ROOT/app/middleware/" || {
                log "WARNING: Failed to copy middleware modules directory"
            }
        fi
        
        # Ensure tenant middleware exists
        if [ -f "app/middleware/tenant.py" ]; then
            if [ "$AZURE_ROOT" = "." ]; then
                log "✓ Tenant middleware present: tenant.py"
            else
                safe_copy "app/middleware/tenant.py" "$AZURE_ROOT/app/middleware/tenant.py" "tenant middleware"
            fi
        else
            log "ERROR: Missing critical file: app/middleware/tenant.py"
            return 1
        fi
    else
        log "ERROR: app/middleware directory not found!"
        return 1
    fi
    
    # Copy other important app modules
    app_modules=(
        "app/__init__.py"
        "app/main.py"
        "app/main_saas.py"
        "app/config.py"
    )
    
    for file in "${app_modules[@]}"; do
        if [ -f "$file" ]; then
            if [ "$AZURE_ROOT" = "." ]; then
                log "✓ App module present: $(basename $file)"
            else
                safe_copy "$file" "$AZURE_ROOT/$file" "app module $(basename $file)"
            fi
        else
            log "WARNING: Missing app module: $file"
        fi
    done
    
    # Copy schemas
    if [ -d "app/schemas" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping schemas modules copy (files already in place)"
        else
            log "Copying schemas modules directory..."
            cp -r "app/schemas/." "$AZURE_ROOT/app/schemas/" || {
                log "WARNING: Failed to copy schemas modules directory"
            }
        fi
    else
        log "WARNING: app/schemas directory not found"
    fi
    
    # Copy auth modules
    if [ -d "app/auth" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping auth modules copy (files already in place)"
        else
            log "Copying auth modules directory..."
            cp -r "app/auth/." "$AZURE_ROOT/app/auth/" || {
                log "WARNING: Failed to copy auth modules directory"
            }
        fi
    else
        log "WARNING: app/auth directory not found"
    fi
    
    # Copy subscription modules
    if [ -d "app/subscription" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping subscription modules copy (files already in place)"
        else
            log "Copying subscription modules directory..."
            cp -r "app/subscription/." "$AZURE_ROOT/app/subscription/" || {
                log "WARNING: Failed to copy subscription modules directory"
            }
        fi
    else
        log "WARNING: app/subscription directory not found"
    fi
    
    # Copy state management modules
    if [ -d "app/state" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping state management modules copy (files already in place)"
        else
            log "Copying state management modules directory..."
            cp -r "app/state/." "$AZURE_ROOT/app/state/" || {
                log "WARNING: Failed to copy state management modules directory"
            }
        fi
    else
        log "WARNING: app/state directory not found"
    fi
    
    # Copy web modules
    if [ -d "app/web" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping web modules copy (files already in place)"
        else
            log "Copying web modules directory..."
            cp -r "app/web/." "$AZURE_ROOT/app/web/" || {
                log "WARNING: Failed to copy web modules directory"
            }
        fi
    else
        log "WARNING: app/web directory not found"
    fi
    
    # Copy diagnostic files
    if [ "$AZURE_ROOT" = "." ]; then
        log "Local environment detected - skipping diagnostic and config files copy (files already in place)"
    else
        log "Copying diagnostic and deployment files..."
        
        diagnostic_files=(
            "azure_import_diagnostics.py"
            "app_adapter_azure_agents_fixed.py"
            "validate_agent_imports.py"
            "agent_fallback_system.py"
        )
        
        for file in "${diagnostic_files[@]}"; do
            if [ -f "$file" ]; then
                safe_copy "$file" "$AZURE_ROOT/$file" "diagnostic file $(basename $file)"
            else
                log "WARNING: Missing diagnostic file: $file"
            fi
        done
        
        # Copy configuration files
        config_files=(
            "requirements.txt"
            "requirements_azure_agents.txt"
            "requirements_complete.txt"
            ".env.example"
            ".env.saas.example"
            "alembic.ini"
            "langgraph.json"
        )
        
        for file in "${config_files[@]}"; do
            if [ -f "$file" ]; then
                safe_copy "$file" "$AZURE_ROOT/$file" "config file $(basename $file)"
            else
                log "WARNING: Missing config file: $file"
            fi
        done
    fi
    
    # Copy migration files
    if [ -d "migrations" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping migrations copy (files already in place)"
        else
            log "Copying migrations directory..."
            cp -r "migrations/." "$AZURE_ROOT/migrations/" || {
                log "WARNING: Failed to copy migrations directory"
            }
        fi
    else
        log "WARNING: migrations directory not found"
    fi
    
    # Copy scripts
    if [ -d "scripts" ]; then
        if [ "$AZURE_ROOT" = "." ]; then
            log "Local environment detected - skipping scripts copy (files already in place)"
        else
            log "Copying scripts directory..."
            cp -r "scripts/." "$AZURE_ROOT/scripts/" || {
                log "WARNING: Failed to copy scripts directory"
            }
        fi
    else
        log "WARNING: scripts directory not found"
    fi
    
    # Set Python path environment variables
    log "Setting Python path environment variables..."
    
    python_paths=(
        "$AZURE_ROOT"
        "$AZURE_ROOT/app"
        "$AZURE_ROOT/app/agents"
        "$AZURE_ROOT/app/graphs"
        "$AZURE_ROOT/app/tools"
        "$AZURE_ROOT/app/utils"
        "$AZURE_ROOT/app/db"
        "$AZURE_ROOT/app/middleware"
    )
    
    # Create Python path string
    PYTHON_PATH_STRING=$(IFS=:; echo "${python_paths[*]}")
    
    # Set environment variable (this will be available for the current session)
    export PYTHONPATH="$PYTHON_PATH_STRING"
    log "PYTHONPATH set to: $PYTHONPATH"
    
    # Create a startup script that sets the Python path
    startup_script="$AZURE_ROOT/set_python_path.sh"
    log "Creating Python path startup script: $startup_script"
    
    cat > "$startup_script" << EOF
#!/bin/bash
# Auto-generated Python path setup for Azure deployment
export PYTHONPATH="$PYTHON_PATH_STRING"
echo "Python path configured: \$PYTHONPATH"
EOF
    
    chmod +x "$startup_script"
    
    # Set file permissions
    log "Setting file permissions..."
    
    # Set general permissions
    set_permissions "$AZURE_ROOT/app" "755"
    
    # Set executable permissions for Python files
    if command_exists find; then
        find "$AZURE_ROOT" -name "*.py" -type f -exec chmod 644 {} \; 2>/dev/null || log "WARNING: Could not set Python file permissions"
        find "$AZURE_ROOT" -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || log "WARNING: Could not set shell script permissions"
    fi
    
    # Validate deployment by running diagnostics
    log "Running import diagnostics to validate deployment..."
    
    if [ -f "$AZURE_ROOT/azure_import_diagnostics.py" ]; then
        cd "$AZURE_ROOT"
        python azure_import_diagnostics.py || {
            log "WARNING: Diagnostics failed, but continuing deployment"
        }
        cd - > /dev/null
    else
        log "WARNING: Diagnostic script not found, skipping validation"
    fi
    
    # Create deployment summary
    log "Creating deployment summary..."
    
    summary_file="$AZURE_ROOT/deployment_summary.txt"
    cat > "$summary_file" << EOF
Azure Agent Deployment Summary
==============================
Deployment Date: $(date)
Environment: Azure App Service
Deployment Script: azure-deploy-agents-fixed.sh

Directories Created:
$(for dir in "${directories[@]}"; do echo "  - $dir"; done)

Key Files Deployed:
  - app_adapter_azure_agents_fixed.py (Enhanced app adapter)
  - azure_import_diagnostics.py (Diagnostic system)
  - Agent modules in app/agents/
  - Graph modules in app/graphs/
  - Database modules in app/db/
  - Middleware modules in app/middleware/
  - Utility modules in app/utils/

Python Path Configuration:
  PYTHONPATH=$PYTHON_PATH_STRING

Next Steps:
1. Verify all environment variables are set
2. Run health check: GET /api/agents/health
3. Run diagnostics: GET /api/agents/diagnostics
4. Test agent functionality: POST /api/agents/chat

Troubleshooting:
- Check deployment_summary.txt for deployment details
- Run azure_import_diagnostics.py for detailed import analysis
- Check application logs for runtime errors
- Verify database connectivity and environment variables
EOF
    
    log "Deployment summary created: $summary_file"
    
    # Final validation
    log "Performing final validation..."
    
    critical_files=(
        "$AZURE_ROOT/app/agents/api_router.py"
        "$AZURE_ROOT/app/agents/agent_factory.py"
        "$AZURE_ROOT/app/db/session.py"
        "$AZURE_ROOT/app/middleware/tenant.py"
        "$AZURE_ROOT/app_adapter_azure_agents_fixed.py"
        "$AZURE_ROOT/azure_import_diagnostics.py"
    )
    
    missing_critical=0
    for file in "${critical_files[@]}"; do
        if [ ! -f "$file" ]; then
            log "ERROR: Critical file missing: $file"
            missing_critical=$((missing_critical + 1))
        else
            log "✓ Critical file present: $(basename $file)"
        fi
    done
    
    if [ $missing_critical -gt 0 ]; then
        log "ERROR: $missing_critical critical files are missing!"
        log "Deployment may not function correctly."
        return 1
    fi
    
    log "=== Deployment Complete ==="
    log "✓ All critical files deployed successfully"
    log "✓ Directory structure created"
    log "✓ Permissions set"
    log "✓ Python path configured"
    log "✓ Diagnostic tools available"
    
    echo ""
    echo "Deployment Summary:"
    echo "  - Environment: Azure App Service"
    echo "  - Root Path: $AZURE_ROOT"
    echo "  - Python Path: $PYTHON_PATH_STRING"
    echo "  - Critical Files: All present"
    echo "  - Status: SUCCESS"
    echo ""
    echo "Next Steps:"
    echo "  1. Start the application with the new adapter"
    echo "  2. Check health endpoint: /api/agents/health"
    echo "  3. Run diagnostics: /api/agents/diagnostics"
    echo "  4. Monitor logs for any import issues"
    echo ""
    
    return 0
}

# Error handling
trap 'log "ERROR: Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"
exit_code=$?

if [ $exit_code -eq 0 ]; then
    log "Deployment completed successfully!"
else
    log "Deployment failed with exit code: $exit_code"
fi

exit $exit_code
