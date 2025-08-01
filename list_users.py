#!/usr/bin/env python3
"""
Script para listar todos los usuarios de la base de datos
"""

import asyncio
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl

async def list_all_users():
    """Lista todos los usuarios de la base de datos"""
    db = SessionLocal()
    try:
        user_repository = UserRepositoryImpl(db)
        users = await user_repository.get_all()
        
        if not users:
            print("No hay usuarios registrados en la base de datos.")
            return
        
        print(f"\n{'='*60}")
        print(f"LISTA DE USUARIOS ({len(users)} usuarios)")
        print(f"{'='*60}")
        
        for i, user in enumerate(users, 1):
            print(f"\n{i}. Usuario ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Activo: {'Sí' if user.is_active else 'No'}")
            print(f"   Creado: {user.created_at}")
            if user.updated_at:
                print(f"   Actualizado: {user.updated_at}")
            print(f"   {'-'*40}")
            
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(list_all_users()) 