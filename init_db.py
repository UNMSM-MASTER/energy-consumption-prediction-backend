#!/usr/bin/env python3
"""
Script para inicializar la base de datos y crear las tablas.
Este script debe ejecutarse después de que PostgreSQL esté corriendo.
"""

import os
import sys
from sqlalchemy import create_engine
from decouple import config

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.database import Base
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.database.models.prediction_model import PredictionModel

def init_database():
    """Inicializar la base de datos creando todas las tablas"""
    try:
        # Obtener la URL de la base de datos desde las variables de entorno
        database_url = config("DATABASE_URL", default="postgresql://postgres:password@localhost:5432/energy_prediction")
        
        print(f"Conectando a la base de datos: {database_url}")
        
        # Crear el engine
        engine = create_engine(database_url)
        
        # Crear todas las tablas
        print("Creando tablas...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Base de datos inicializada correctamente")
        print("✅ Tablas creadas:")
        print("   - users")
        print("   - predictions")
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Inicializando base de datos...")
    init_database() 