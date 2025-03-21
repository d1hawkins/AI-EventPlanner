FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for MCP servers
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (excluding optional google group and dev dependencies)
RUN poetry install --without google --without dev --no-root --no-interaction --no-ansi

# Copy application code
COPY . .

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting application..."\n\
echo "Environment: DATABASE_URL=${DATABASE_URL}"\n\
echo "Environment: LLM_PROVIDER=${LLM_PROVIDER}"\n\
echo "Checking if OpenAI API key is set: ${OPENAI_API_KEY:+true}"\n\
\n\
# Start MCP servers in background\n\
echo "Starting SendGrid MCP server..."\n\
node /app/mcp-servers/sendgrid-mcp/build/index.js &\n\
SENDGRID_PID=$!\n\
\n\
echo "Starting OpenWeather MCP server..."\n\
node /app/mcp-servers/openweather-mcp/build/index.js &\n\
OPENWEATHER_PID=$!\n\
\n\
# Setup trap to kill MCP servers on exit\n\
trap "kill $SENDGRID_PID $OPENWEATHER_PID" EXIT\n\
\n\
echo "Starting main application server..."\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Install MCP server dependencies
WORKDIR /app/mcp-servers/sendgrid-mcp
RUN npm install
WORKDIR /app/mcp-servers/openweather-mcp
RUN npm install
WORKDIR /app

# Run the application
CMD ["/app/start.sh"]
