# Testing the AI Event Planner SaaS Locally

## Current Setup

We have two components running:

1. **Static File Server** (Port 8001)
   - Running with: `python serve_saas_static_alt.py`
   - Serves the frontend static files
   - URL: http://localhost:8001/saas/

2. **Simplified Backend API** (Port 8002)
   - Running with: `python3 run_saas_no_docker.py`
   - Provides basic API endpoints
   - URL: http://localhost:8002/

## How to Test

1. Access the frontend at: http://localhost:8001/saas/
2. Navigate through the UI to test the frontend functionality
3. The backend API is available at http://localhost:8002/ for any API calls

## Known Limitations

- The agent integration is not fully functional due to dependency issues
- Some API endpoints may return 404 errors when called from the frontend
- Database operations are using a local SQLite database instead of PostgreSQL

## Troubleshooting

If you encounter issues:

1. Check that both servers are running in their respective terminals
2. Verify that the ports (8001 and 8002) are not being used by other applications
3. Check the browser console for any JavaScript errors
4. Check the terminal output for any server errors

## Next Steps

To fully enable the agent integration, additional work would be needed:

1. Resolve the Pydantic version compatibility issues (current version: 2.11.4)
2. Update the coordinator_graph.py file to work with Pydantic v2
3. Install additional dependencies for the agent system

For now, you can test the frontend functionality and basic API endpoints with the current setup.
