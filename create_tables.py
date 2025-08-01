#!/usr/bin/env python3
"""
Script to create database tables directly using SQLAlchemy.
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append('/app')

from app.config.database import Base
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.database.models.prediction_model import PredictionModel

def main():
    # Database URL for Docker environment
    database_url = "postgresql://postgres:password@postgres:5432/energy_prediction"
    
    # Create engine
    engine = create_engine(database_url)
    
    # Create all tables
    print(f"Creating tables in database: {database_url}")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Test connection
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        # Test query
        result = session.execute("SELECT 1")
        print("Database connection test successful!")
    except Exception as e:
        print(f"Database connection test failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main() 