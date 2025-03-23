#!/usr/bin/env python3
"""
Serve the static files for the AI Event Planner SaaS application.
This script starts a simple HTTP server to serve the static files.
"""

import os
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path

# Ensure we're in the project root directory
project_root = Path(__file__).resolve().parent
os.chdir(project_root)

# Configuration
PORT = 8090
DIRECTORY = "app/web/static"

class Handler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for serving static files."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        # Redirect root to SaaS index page
        if self.path == '/':
            self.path = '/saas/index.html'
        # Rewrite paths that start with /static/saas/ to /saas/
        elif self.path.startswith('/static/saas/'):
            self.path = self.path.replace('/static/saas/', '/saas/')
        return super().do_GET()

def main():
    """Main function."""
    print(f"Starting static file server for AI Event Planner SaaS on port {PORT}...")
    
    # Check if the static directory exists
    static_dir = project_root / DIRECTORY
    if not static_dir.exists():
        print(f"Error: Static directory '{DIRECTORY}' does not exist.")
        return 1
    
    # Check if the SaaS index page exists
    saas_index = static_dir / "saas" / "index.html"
    if not saas_index.exists():
        print(f"Error: SaaS index page '{saas_index}' does not exist.")
        return 1
    
    # Start the server
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Server started at http://localhost:{PORT}")
            print(f"SaaS application available at http://localhost:{PORT}/saas/index.html")
            
            # Open the browser
            webbrowser.open(f"http://localhost:{PORT}/saas/index.html")
            
            # Serve until interrupted
            print("Press Ctrl+C to stop the server...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
