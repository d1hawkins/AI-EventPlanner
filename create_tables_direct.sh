#!/bin/bash
# Create database tables directly without relying on migrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Make the script executable
chmod +x scripts/create_tables_direct.py

# Install required packages
echo "Installing required packages..."
pip install sqlalchemy psycopg2-binary

# Ask for database connection details
read -p "Enter database server name (e.g., ai-event-planner-db.postgres.database.azure.com): " DB_SERVER
read -p "Enter database name (default: eventplanner): " DB_NAME
DB_NAME=${DB_NAME:-eventplanner}
read -p "Enter database username: " DB_USER
read -s -p "Enter database password: " DB_PASSWORD
echo ""

# Set environment variables
export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_SERVER}:5432/${DB_NAME}"

# Run the direct table creation script
echo -e "${YELLOW}Creating database tables directly...${NC}"
python scripts/create_tables_direct.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database tables created successfully.${NC}"
else
    echo -e "${RED}Failed to create database tables.${NC}"
    echo "Trying alternative approach..."
    
    # Try an alternative approach using psql
    echo "Do you want to try creating tables using psql? (y/n)"
    read USE_PSQL
    
    if [[ "$USE_PSQL" == "y" || "$USE_PSQL" == "Y" ]]; then
        # Create a temporary SQL file
        SQL_FILE=$(mktemp)
        
        # Write SQL commands to create tables
        cat > $SQL_FILE << 'EOF'
-- Create tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    full_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    location VARCHAR(255),
    organization_id INTEGER REFERENCES organizations(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    agent_type VARCHAR(50),
    title VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    organization_id INTEGER REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    content TEXT,
    role VARCHAR(20),
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    price FLOAT,
    features TEXT,
    tier VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    plan_id INTEGER REFERENCES subscription_plans(id),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS user_organizations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    organization_id INTEGER REFERENCES organizations(id),
    role VARCHAR(50)
);
EOF
        
        # Run psql
        echo "Running psql to create tables..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_SERVER -U $DB_USER -d $DB_NAME -f $SQL_FILE
        
        # Clean up
        rm $SQL_FILE
        
        echo -e "${GREEN}Tables created using psql.${NC}"
    fi
fi

echo "Done."
