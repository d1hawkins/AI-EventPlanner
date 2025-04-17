from flask import Flask, request, Response
import requests
import subprocess
import threading
import os
import time

# Install required packages
subprocess.call(["./install_packages.sh"], shell=True)

# Create a Flask application
app = Flask(__name__)

# Define the FastAPI application URL (running locally)
FASTAPI_URL = "http://localhost:8001"  # FastAPI will run on a different port

# Start the FastAPI application in a separate process
def run_fastapi():
    # Wait a moment to ensure packages are installed
    time.sleep(2)
    subprocess.Popen(["gunicorn", "app_simplified:app", "--bind", "0.0.0.0:8001", "--workers", "2"])

# Start FastAPI in a separate thread
threading.Thread(target=run_fastapi, daemon=True).start()

# Create a simple route that returns a static response
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Event Planner</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f5f5f5;
            }
            .container {
                text-align: center;
                padding: 20px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
            }
            p {
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Event Planner</h1>
            <p>Welcome to the AI Event Planner application!</p>
            <p>This application is running on Azure App Service without Docker.</p>
        </div>
    </body>
    </html>
    """

# Create a proxy route that forwards all requests to the FastAPI application
@app.route('/<path:path>')
def proxy(path):
    try:
        # Forward the request to the FastAPI application
        url = f"{FASTAPI_URL}/{path}"
        
        # Forward the request method, headers, and body
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )
        
        # Create a Flask response from the FastAPI response
        response = Response(
            resp.iter_content(chunk_size=10*1024),
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'text/html')
        )
        
        # Add headers from the FastAPI response
        for key, value in resp.headers.items():
            if key.lower() not in ('content-length', 'content-encoding', 'transfer-encoding'):
                response.headers[key] = value
        
        return response
    except Exception as e:
        return f"Error: {str(e)}", 500

# Health check endpoint
@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
