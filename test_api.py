#!/usr/bin/env python3
"""
Script para probar la API después de la migración a arquitectura hexagonal.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Probar el endpoint de health check"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check exitoso")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Health check falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en health check: {e}")

def test_register_user():
    """Probar el registro de usuario"""
    print("\n🔍 Probando registro de usuario...")
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            print("✅ Registro de usuario exitoso")
            user_info = response.json()
            print(f"   Usuario creado: {user_info['username']}")
            return user_info
        else:
            print(f"❌ Registro falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return None

def test_login(user_data):
    """Probar el login"""
    print("\n🔍 Probando login...")
    try:
        login_data = {
            "username": user_data["username"],
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if response.status_code == 200:
            print("✅ Login exitoso")
            token_info = response.json()
            print(f"   Token obtenido: {token_info['access_token'][:20]}...")
            return token_info["access_token"]
        else:
            print(f"❌ Login falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_create_prediction(token, user_id):
    """Probar la creación de predicción"""
    print("\n🔍 Probando creación de predicción...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        prediction_data = {
            "user_id": user_id,
            "target_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "model_version": "v1.0",
            "features_used": ["hour", "dayofweek", "month", "year"]
        }
        response = requests.post(f"{BASE_URL}/predictions/", json=prediction_data, headers=headers)
        if response.status_code == 200:
            print("✅ Creación de predicción exitosa")
            prediction_info = response.json()
            print(f"   Predicción ID: {prediction_info['id']}")
            print(f"   Consumo predicho: {prediction_info['consumption_prediction']}")
            return prediction_info
        else:
            print(f"❌ Creación de predicción falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en creación de predicción: {e}")
        return None

def test_get_user_predictions(token, user_id):
    """Probar obtener predicciones de usuario"""
    print("\n🔍 Probando obtener predicciones de usuario...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/predictions/user/{user_id}", headers=headers)
        if response.status_code == 200:
            predictions = response.json()
            print(f"✅ Obtención de predicciones exitosa")
            print(f"   Número de predicciones: {len(predictions)}")
            return predictions
        else:
            print(f"❌ Obtención de predicciones falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo predicciones: {e}")
        return None

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas de la API...")
    print("=" * 50)
    
    # Probar health check
    test_health_check()
    
    # Probar registro de usuario
    user_data = test_register_user()
    if not user_data:
        print("❌ No se pudo crear usuario, abortando pruebas")
        return
    
    # Probar login
    token = test_login(user_data)
    if not token:
        print("❌ No se pudo obtener token, abortando pruebas")
        return
    
    # Probar creación de predicción
    prediction_data = test_create_prediction(token, user_data["id"])
    if not prediction_data:
        print("❌ No se pudo crear predicción, abortando pruebas")
        return
    
    # Probar obtener predicciones
    test_get_user_predictions(token, user_data["id"])
    
    print("\n" + "=" * 50)
    print("✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 