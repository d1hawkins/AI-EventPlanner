#!/usr/bin/env python3
"""
Simple HTTP server for serving static files for the AI Event Planner SaaS application.
This is for development and testing purposes only.
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, unquote

PORT = 8000
DIRECTORY = "app/web/static"

class SaaSHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for the SaaS application."""
    
    def log_message(self, format, *args):
        """Log messages with additional information."""
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))
        
        # Add additional debugging information
        if args and isinstance(args[0], str) and args[0].startswith("GET"):
            path = args[0].split()[1]
            translated_path = self.translate_path(path)
            sys.stderr.write("Requested path: %s\n" % path)
            sys.stderr.write("Translated to: %s\n" % translated_path)
            sys.stderr.write("File exists: %s\n" % os.path.exists(translated_path))
    
    def translate_path(self, path):
        """Translate URL path to file system path."""
        # Parse the URL
        parsed_path = urlparse(path)
        # Unquote the path
        path = unquote(parsed_path.path)
        
        # Handle /saas/ URLs
        if path.startswith('/saas/'):
            # Remove the /saas/ prefix
            path = path[6:]  # Changed from 5 to 6 to correctly handle the path
            # If path is empty or ends with /, serve index.html
            if path == '' or path.endswith('/'):
                path = path + 'index.html'
            # Prepend the directory
            result = os.path.join(DIRECTORY, 'saas', path)
            return result
        
        # Handle /saas URL (without trailing slash)
        if path == '/saas':
            return os.path.join(DIRECTORY, 'saas', 'index.html')
        
        # Handle root URL
        if path == '/':
            return os.path.join(DIRECTORY, 'saas', 'index.html')
        
        # Default behavior
        return super().translate_path(path)
    
    def end_headers(self):
        """Add CORS headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Start the server."""
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if the directory exists
    if not os.path.isdir(DIRECTORY):
        print(f"Error: Directory '{DIRECTORY}' not found.")
        sys.exit(1)
    
    # Check if the saas directory exists
    if not os.path.isdir(os.path.join(DIRECTORY, 'saas')):
        print(f"Error: Directory '{os.path.join(DIRECTORY, 'saas')}' not found.")
        sys.exit(1)
    
    # Print the current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # List the contents of the saas directory
    print(f"Contents of {os.path.join(DIRECTORY, 'saas')}:")
    for item in os.listdir(os.path.join(DIRECTORY, 'saas')):
        print(f"  {item}")
    
    # Start the server
    with socketserver.TCPServer(("", PORT), SaaSHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"SaaS application available at http://localhost:{PORT}/saas/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            httpd.server_close()

if __name__ == "__main__":
    main()
