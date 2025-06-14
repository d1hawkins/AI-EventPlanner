#!/bin/bash
echo "Installing agent dependencies..."
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install sqlalchemy==2.0.23
pip install pydantic==2.5.0
pip install langchain==0.0.350
pip install langgraph==0.0.62
pip install google-generativeai==0.3.2
pip install openai==1.3.7
pip install python-dotenv==1.0.0
pip install psycopg2-binary==2.9.9
pip install alembic==1.13.1
echo "Agent dependencies installed successfully"
