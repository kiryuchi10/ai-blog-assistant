#!/usr/bin/env python3
"""
Database Setup Script for AI Blog Assistant
Creates PostgreSQL database, user, and initializes tables
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import subprocess
from pathlib import Path

# Database configuration from .env
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ai_blog_assistant',
    'user': 'blog_user',
    'password': 'blog_secure_password_2024',
    'admin_user': 'postgres',  # Default PostgreSQL admin user
    'admin_password': '',  # Will prompt if needed
}

def check_postgresql_installed():
    """Check if PostgreSQL is installed and running"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL not found")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not installed or not in PATH")
        return False

def check_postgresql_service():
    """Check if PostgreSQL service is running"""
    try:
        # Try to connect to default postgres database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',
            user=DB_CONFIG['admin_user'],
            password=DB_CONFIG['admin_password']
        )
        conn.close()
        print("✅ PostgreSQL service is running")
        return True
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL service not running or connection failed: {e}")
        return False

def create_database_and_user():
    """Create database and user if they don't exist"""
    try:
        # Connect to PostgreSQL as admin
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',
            user=DB_CONFIG['admin_user'],
            password=DB_CONFIG['admin_password']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (DB_CONFIG['user'],))
        user_exists = cursor.fetchone()

        if not user_exists:
            # Create user
            cursor.execute(f"""
                CREATE USER {DB_CONFIG['user']} 
                WITH PASSWORD '{DB_CONFIG['password']}' 
                CREATEDB LOGIN;
            """)
            print(f"✅ Created user: {DB_CONFIG['user']}")
        else:
            print(f"✅ User already exists: {DB_CONFIG['user']}")

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_CONFIG['database'],))
        db_exists = cursor.fetchone()

        if not db_exists:
            # Create database
            cursor.execute(f"""
                CREATE DATABASE {DB_CONFIG['database']} 
                OWNER {DB_CONFIG['user']} 
                ENCODING 'UTF8';
            """)
            print(f"✅ Created database: {DB_CONFIG['database']}")
        else:
            print(f"✅ Database already exists: {DB_CONFIG['database']}")

        # Grant privileges
        cursor.execute(f"""
            GRANT ALL PRIVILEGES ON DATABASE {DB_CONFIG['database']} 
            TO {DB_CONFIG['user']};
        """)
        print(f"✅ Granted privileges to {DB_CONFIG['user']}")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_tables():
    """Create application tables"""
    try:
        # Connect to the application database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()

        # Create tables
        tables_sql = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            subscription_tier VARCHAR(50) DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Content table
        CREATE TABLE IF NOT EXISTS content (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(500) NOT NULL,
            content TEXT NOT NULL,
            content_type VARCHAR(50) DEFAULT 'blog_post',
            format VARCHAR(50) DEFAULT 'markdown',
            tone VARCHAR(50) DEFAULT 'professional',
            status VARCHAR(50) DEFAULT 'draft',
            word_count INTEGER DEFAULT 0,
            character_count INTEGER DEFAULT 0,
            seo_score FLOAT DEFAULT 0.0,
            readability_score FLOAT DEFAULT 0.0,
            tags TEXT[],
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Templates table
        CREATE TABLE IF NOT EXISTS templates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            content_type VARCHAR(50) NOT NULL,
            template_content TEXT NOT NULL,
            variables JSONB,
            is_public BOOLEAN DEFAULT FALSE,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Analytics table
        CREATE TABLE IF NOT EXISTS analytics (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB,
            ip_address INET,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- API Keys table
        CREATE TABLE IF NOT EXISTS api_keys (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            key_name VARCHAR(255) NOT NULL,
            api_key VARCHAR(255) UNIQUE NOT NULL,
            permissions TEXT[],
            is_active BOOLEAN DEFAULT TRUE,
            last_used_at TIMESTAMP,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Content generations table (for tracking AI generations)
        CREATE TABLE IF NOT EXISTS content_generations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
            prompt TEXT NOT NULL,
            model_used VARCHAR(100),
            tokens_used INTEGER DEFAULT 0,
            generation_time FLOAT DEFAULT 0.0,
            cost DECIMAL(10, 6) DEFAULT 0.0,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_content_user_id ON content(user_id);
        CREATE INDEX IF NOT EXISTS idx_content_created_at ON content(created_at);
        CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
        CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at);
        CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
        CREATE INDEX IF NOT EXISTS idx_content_generations_user_id ON content_generations(user_id);

        -- Create updated_at trigger function
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        -- Create triggers for updated_at
        DROP TRIGGER IF EXISTS update_users_updated_at ON users;
        CREATE TRIGGER update_users_updated_at 
            BEFORE UPDATE ON users 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

        DROP TRIGGER IF EXISTS update_content_updated_at ON content;
        CREATE TRIGGER update_content_updated_at 
            BEFORE UPDATE ON content 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

        DROP TRIGGER IF EXISTS update_templates_updated_at ON templates;
        CREATE TRIGGER update_templates_updated_at 
            BEFORE UPDATE ON templates 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """

        cursor.execute(tables_sql)
        conn.commit()
        print("✅ Database tables created successfully")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"❌ Table creation failed: {e}")
        return False

def setup_redis():
    """Check Redis setup"""
    try:
        import redis
        r = redis.Redis(
            host='localhost',
            port=6379,
            password=DB_CONFIG.get('redis_password', ''),
            decode_responses=True
        )
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("💡 Install Redis: https://redis.io/download")
        return False

def create_demo_data():
    """Create demo user and content"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()

        # Create demo user
        cursor.execute("""
            INSERT INTO users (email, username, password_hash, full_name, is_verified)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
            RETURNING id;
        """, (
            'demo@example.com',
            'demo_user',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJgusgqHu',  # demo123
            'Demo User',
            True
        ))

        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]
            print(f"✅ Created demo user with ID: {user_id}")
        else:
            # Get existing user ID
            cursor.execute("SELECT id FROM users WHERE email = %s", ('demo@example.com',))
            user_id = cursor.fetchone()[0]
            print(f"✅ Demo user already exists with ID: {user_id}")

        # Create demo content
        cursor.execute("""
            INSERT INTO content (user_id, title, content, content_type, format, tone, status, word_count, character_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            user_id,
            'AI Blog Assistant: Automating the Future of Technical Content',
            '''🚀 AI Blog Assistant: Automating the Future of Technical Content

Following up on my goal to build a modular AI-powered innovation lab, I'm excited to introduce the AI Blog Assistant—a tool I built to automate the creation of research summaries, technical blogs, and SEO-ready content.

🧠 Why I Built It
As developers, we spend countless hours digesting technical papers, experimenting, and writing documentation. But sharing our insights publicly often takes a back seat. The AI Blog Assistant solves this by turning structured notes, papers, or ideas into coherent, high-quality blog posts—automatically.

🛠 What It Does
✅ Takes input (bullet points, markdown notes, or PDFs)
✅ Uses GPT to generate summaries, tutorials, or commentary in a chosen tone (explanatory, concise, humorous, etc.)
✅ Automatically embeds key terms, links, and SEO meta-structure
✅ Supports one-click publishing (Notion/Markdown export ready)

📈 Impact on Workflow
✅ Reduced blog creation time by 70%
✅ Enabled daily posting with consistent quality
✅ Increased knowledge retention by forcing structured summarization
✅ Opened the door to multi-language publishing & cross-platform sharing

🌐 Tech Stack
React · GPT API · SEO Schema · Markdown Renderer · Flask Backend (soon to be FastAPI)

Coming soon: integration with arXiv, S2ORC, and image captioning via BLIP

🧩 Part of a Bigger System
This assistant is one module of my broader effort to build plug-and-play tools, including:
📊 AI Stock Sentiment Tracker
🧪 AI-Accelerated DOE for Engineering
🖼 3D MCP Model Generator
🎛 UI Mockup Generator

💬 Let's Share Knowledge Better
I believe tech is best advanced not only by building, but by communicating ideas well. This tool is my attempt to bridge that gap—and I'm happy to open-source it or co-develop it further with researchers, bloggers, and dev teams.

🔗 You can see the project (and others) here: 👉 https://lnkd.in/g2EHhQtd

If this resonates with your work or vision, let's connect.

#AI #BlogAutomation #KnowledgeSharing #MachineLearning #FullStackDevelopment #LLM #SEO #DeveloperTools #OpenSource #InnovationLab #GPT4''',
            'linkedin_post',
            'markdown',
            'professional',
            'published',
            319,
            2102
        ))

        conn.commit()
        print("✅ Demo data created successfully")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"❌ Demo data creation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Blog Assistant Database Setup")
    print("=" * 50)

    # Check PostgreSQL installation
    if not check_postgresql_installed():
        print("\n💡 Install PostgreSQL:")
        print("   Windows: https://www.postgresql.org/download/windows/")
        print("   macOS: brew install postgresql")
        print("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return False

    # Check PostgreSQL service
    if not check_postgresql_service():
        print("\n💡 Start PostgreSQL service:")
        print("   Windows: net start postgresql-x64-14")
        print("   macOS: brew services start postgresql")
        print("   Ubuntu: sudo systemctl start postgresql")
        return False

    # Create database and user
    print("\n📊 Setting up database...")
    if not create_database_and_user():
        return False

    # Create tables
    print("\n🏗️ Creating tables...")
    if not create_tables():
        return False

    # Check Redis
    print("\n🔴 Checking Redis...")
    setup_redis()  # Non-blocking

    # Create demo data
    print("\n🎭 Creating demo data...")
    create_demo_data()

    print("\n🎉 Database setup completed!")
    print("\n📋 Connection Details:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Port: {DB_CONFIG['port']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print(f"   Password: {DB_CONFIG['password']}")

    print("\n🔗 Connection URL:")
    print(f"   postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

    print("\n✅ Ready to start the backend server!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)