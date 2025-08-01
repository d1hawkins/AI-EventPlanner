-- Create and Seed Database for AI Event Planner SaaS
-- This script creates all necessary tables and adds initial seed data

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    location VARCHAR(255),
    organization_id INTEGER REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    agent_type VARCHAR(50),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    organization_id INTEGER REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    content TEXT,
    role VARCHAR(20),  -- 'user' or 'assistant'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS user_organizations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    organization_id INTEGER REFERENCES organizations(id),
    role VARCHAR(50)  -- 'admin', 'member', etc.
);

-- Seed data

-- Insert admin user
INSERT INTO users (email, hashed_password, is_active, is_superuser, full_name)
VALUES (
    'admin@example.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- password: 'password'
    TRUE,
    TRUE,
    'Admin User'
) ON CONFLICT (email) DO NOTHING;

-- Insert default organization
INSERT INTO organizations (name, description, created_at, updated_at)
VALUES (
    'Default Organization',
    'Default organization for the system',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

-- Get the IDs
DO $$
DECLARE
    admin_id INTEGER;
    org_id INTEGER;
BEGIN
    SELECT id INTO admin_id FROM users WHERE email = 'admin@example.com';
    SELECT id INTO org_id FROM organizations WHERE name = 'Default Organization';
    
    -- Insert user-organization relationship
    IF admin_id IS NOT NULL AND org_id IS NOT NULL THEN
        INSERT INTO user_organizations (user_id, organization_id, role)
        VALUES (admin_id, org_id, 'admin')
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- Insert subscription plans
INSERT INTO subscription_plans (name, description, price, features, tier)
VALUES 
    ('Free', 'Basic plan with limited features', 0.00, 'Coordinator and Resource Planning agents', 'free'),
    ('Professional', 'Professional plan with more features', 19.99, 'All agents except Analytics', 'professional'),
    ('Enterprise', 'Enterprise plan with all features', 49.99, 'All agents and features', 'enterprise')
ON CONFLICT (name) DO NOTHING;

-- Get the organization ID and plan ID
DO $$
DECLARE
    org_id INTEGER;
    plan_id INTEGER;
BEGIN
    SELECT id INTO org_id FROM organizations WHERE name = 'Default Organization';
    SELECT id INTO plan_id FROM subscription_plans WHERE name = 'Enterprise';
    
    -- Insert subscription
    IF org_id IS NOT NULL AND plan_id IS NOT NULL THEN
        INSERT INTO subscriptions (organization_id, plan_id, start_date, end_date, is_active)
        VALUES (org_id, plan_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1 year', TRUE)
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- Insert sample events
DO $$
DECLARE
    org_id INTEGER;
BEGIN
    SELECT id INTO org_id FROM organizations WHERE name = 'Default Organization';
    
    IF org_id IS NOT NULL THEN
        INSERT INTO events (title, description, start_date, end_date, location, organization_id, created_at, updated_at)
        VALUES 
            ('Annual Conference', 'Our annual company conference', CURRENT_TIMESTAMP + INTERVAL '30 days', CURRENT_TIMESTAMP + INTERVAL '32 days', 'Convention Center', org_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Team Building', 'Team building event', CURRENT_TIMESTAMP + INTERVAL '15 days', CURRENT_TIMESTAMP + INTERVAL '15 days', 'City Park', org_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
            ('Product Launch', 'New product launch event', CURRENT_TIMESTAMP + INTERVAL '45 days', CURRENT_TIMESTAMP + INTERVAL '45 days', 'Main Office', org_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- Insert sample conversations and messages
DO $$
DECLARE
    user_id INTEGER;
    org_id INTEGER;
    conv_id INTEGER;
BEGIN
    SELECT id INTO user_id FROM users WHERE email = 'admin@example.com';
    SELECT id INTO org_id FROM organizations WHERE name = 'Default Organization';
    
    IF user_id IS NOT NULL AND org_id IS NOT NULL THEN
        -- Insert conversation
        INSERT INTO conversations (user_id, agent_type, title, created_at, updated_at, organization_id)
        VALUES (user_id, 'coordinator', 'Initial Planning', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, org_id)
        RETURNING id INTO conv_id;
        
        -- Insert messages
        IF conv_id IS NOT NULL THEN
            INSERT INTO messages (conversation_id, content, role, created_at)
            VALUES 
                (conv_id, 'I need help planning a conference for 200 people.', 'user', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
                (conv_id, 'I''d be happy to help you plan a conference for 200 people. Let''s start by discussing your requirements. What is the purpose of the conference and when would you like to hold it?', 'assistant', CURRENT_TIMESTAMP - INTERVAL '59 minutes'),
                (conv_id, 'It''s a tech conference in September. We need a venue, catering, and speakers.', 'user', CURRENT_TIMESTAMP - INTERVAL '58 minutes'),
                (conv_id, 'Great! For a tech conference in September for 200 people, I''ll help you organize the venue, catering, and speakers. Let me start by creating a project plan and timeline for this event.', 'assistant', CURRENT_TIMESTAMP - INTERVAL '57 minutes');
        END IF;
    END IF;
END $$;

-- Verify tables were created and seeded
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL
SELECT 'organizations', COUNT(*) FROM organizations
UNION ALL
SELECT 'events', COUNT(*) FROM events
UNION ALL
SELECT 'conversations', COUNT(*) FROM conversations
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'subscription_plans', COUNT(*) FROM subscription_plans
UNION ALL
SELECT 'subscriptions', COUNT(*) FROM subscriptions
UNION ALL
SELECT 'user_organizations', COUNT(*) FROM user_organizations;
