#!/usr/bin/env python3
"""
Script to run Alembic migrations with the correct database URL for Docker environment.
"""
import os
import sys
from alembic.config import Config
from alembic import command

def main():
    # Set the correct database URL for Docker environment
    database_url = "postgresql://postgres:password@postgres:5432/energy_prediction"
    
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    # Run the migration
    print(f"Running migrations with database URL: {database_url}")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully!")

if __name__ == "__main__":
    main() 