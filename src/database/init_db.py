"""
Database initialization script.
"""
import argparse
import os
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import modules
src_dir = Path(__file__).parent.parent
sys.path.append(str(src_dir.parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

from src.database.models import Base, User
from src.database.session import SessionLocal, init_db

# Load environment variables
load_dotenv()


def setup_database():
    """
    Set up the database and create tables.
    """
    # Initialize database tables
    init_db()
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Check if we already have users (to avoid duplicate setup)
        user_count = db.query(User).count()
        if user_count == 0:
            print("Creating initial admin user...")
            # Create an admin user (in a real app, you'd use proper password hashing)
            admin_user = User(
                email="admin@example.com",
                password_hash="hashed_password",  # This should be properly hashed!
                first_name="Admin",
                last_name="User",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully!")
        else:
            print(f"Database already contains {user_count} users. Skipping initial user creation.")
    except Exception as e:
        print(f"Error setting up database: {e}")
        db.rollback()
    finally:
        db.close()


def create_db(db_name):
    """
    Create the database if it doesn't exist.
    """
    # Connect to PostgreSQL without specifying a database to create one
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    
    # Connect to default 'postgres' database
    default_conn_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
    engine = create_engine(default_conn_str)
    
    connection = engine.connect()
    # Set autocommit mode
    connection.execute("commit")
    
    try:
        # Create the database if it doesn't exist
        connection.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully!")
    except ProgrammingError:
        print(f"Database '{db_name}' already exists.")
    finally:
        connection.close()
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument("--create", action="store_true", help="Create the database if it doesn't exist")
    args = parser.parse_args()
    
    db_name = os.getenv("DB_NAME", "investment_saas")
    
    if args.create:
        create_db(db_name)
    
    setup_database()
    print("Database initialization completed.")