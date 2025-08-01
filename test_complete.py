#!/usr/bin/env python3
"""
Script completo de pruebas para la API de Energy Consumption Prediction.
Este script se ejecuta dentro del contenedor Docker.
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuración
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Imprimir una sección con formato"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️  {message}")

def test_health_check():
    """Probar el endpoint de health check"""
    print_section("HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success("Health check exitoso")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print_error(f"Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en health check: {e}")
        return False

def test_root_endpoint():
    """Probar el endpoint raíz"""
    print_section("ENDPOINT RAÍZ")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success("Endpoint raíz exitoso")
            data = response.json()
            print(f"   Mensaje: {data['message']}")
            print(f"   Versión: {data['version']}")
            print(f"   Arquitectura: {data['architecture']}")
            return True
        else:
            print_error(f"Endpoint raíz falló: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en endpoint raíz: {e}")
        return False

def test_register_user(username, email, password):
    """Probar el registro de usuario"""
    print_section(f"REGISTRO DE USUARIO: {username}")
    try:
        user_data = {
            "username": username,
            "email": email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            print_success("Registro de usuario exitoso")
            user_info = response.json()
            print(f"   ID: {user_info['id']}")
            print(f"   Usuario: {user_info['username']}")
            print(f"   Email: {user_info['email']}")
            return user_info
        else:
            print_error(f"Registro falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error en registro: {e}")
        return None

def test_login(username, password):
    """Probar el login"""
    print_section(f"LOGIN: {username}")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if response.status_code == 200:
            print_success("Login exitoso")
            token_info = response.json()
            print(f"   Token obtenido: {token_info['access_token'][:20]}...")
            return token_info["access_token"]
        else:
            print_error(f"Login falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error en login: {e}")
        return None

def test_get_user_info(token):
    """Probar obtener información del usuario"""
    print_section("INFORMACIÓN DEL USUARIO")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print_success("Información de usuario obtenida")
            user_info = response.json()
            print(f"   ID: {user_info['id']}")
            print(f"   Usuario: {user_info['username']}")
            print(f"   Email: {user_info['email']}")
            print(f"   Activo: {user_info['is_active']}")
            return user_info
        else:
            print_error(f"Obtener información falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error al obtener información: {e}")
        return None

def test_create_prediction(token, user_id):
    """Probar la creación de predicción"""
    print_section("CREACIÓN DE PREDICCIÓN")
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
            print_success("Creación de predicción exitosa")
            prediction_info = response.json()
            print(f"   ID: {prediction_info['id']}")
            print(f"   Consumo predicho: {prediction_info['consumption_prediction']}")
            print(f"   Fecha objetivo: {prediction_info['target_date']}")
            return prediction_info
        else:
            print_error(f"Creación de predicción falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error en creación de predicción: {e}")
        return None

def test_get_user_predictions(token, user_id):
    """Probar obtener predicciones de usuario"""
    print_section("PREDICCIONES DEL USUARIO")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/predictions/user/{user_id}", headers=headers)
        if response.status_code == 200:
            print_success("Predicciones obtenidas")
            predictions = response.json()
            print(f"   Total de predicciones: {len(predictions)}")
            for i, pred in enumerate(predictions[:3]):  # Mostrar solo las primeras 3
                print(f"   Predicción {i+1}: ID={pred['id']}, Consumo={pred['consumption_prediction']}")
            return predictions
        else:
            print_error(f"Obtener predicciones falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error al obtener predicciones: {e}")
        return None

def test_date_range_predictions(token):
    """Probar obtener predicciones por rango de fechas"""
    print_section("PREDICCIONES POR RANGO DE FECHAS")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=60)).isoformat()
        
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        response = requests.get(f"{BASE_URL}/predictions/date-range/", params=params, headers=headers)
        if response.status_code == 200:
            print_success("Predicciones por rango obtenidas")
            predictions = response.json()
            print(f"   Total de predicciones: {len(predictions)}")
            return predictions
        else:
            print_error(f"Obtener predicciones por rango falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error al obtener predicciones por rango: {e}")
        return None

def test_clear_cache(token, user_id):
    """Probar limpiar cache de usuario"""
    print_section("LIMPIAR CACHE")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{BASE_URL}/predictions/user/{user_id}/cache", headers=headers)
        if response.status_code == 200:
            print_success("Cache limpiado exitosamente")
            return True
        else:
            print_error(f"Limpiar cache falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error al limpiar cache: {e}")
        return False

def main():
    """Función principal que ejecuta todas las pruebas"""
    print_section("INICIO DE PRUEBAS COMPLETAS")
    print_info("Iniciando pruebas de la API de Energy Consumption Prediction")
    
    # Lista para almacenar resultados
    results = []
    
    # 1. Health check
    results.append(("Health Check", test_health_check()))
    
    # 2. Endpoint raíz
    results.append(("Endpoint Raíz", test_root_endpoint()))
    
    # 3. Registrar usuario
    user_info = test_register_user("testuser", "test@example.com", "testpassword123")
    results.append(("Registro de Usuario", user_info is not None))
    
    if user_info:
        # 4. Login
        token = test_login("testuser", "testpassword123")
        results.append(("Login", token is not None))
        
        if token:
            # 5. Obtener información del usuario
            user_info_me = test_get_user_info(token)
            results.append(("Información de Usuario", user_info_me is not None))
            
            # 6. Crear predicción
            prediction = test_create_prediction(token, user_info['id'])
            results.append(("Crear Predicción", prediction is not None))
            
            # 7. Obtener predicciones del usuario
            predictions = test_get_user_predictions(token, user_info['id'])
            results.append(("Obtener Predicciones", predictions is not None))
            
            # 8. Obtener predicciones por rango de fechas
            range_predictions = test_date_range_predictions(token)
            results.append(("Predicciones por Rango", range_predictions is not None))
            
            # 9. Limpiar cache
            cache_cleared = test_clear_cache(token, user_info['id'])
            results.append(("Limpiar Cache", cache_cleared))
    
    # Resumen final
    print_section("RESUMEN DE PRUEBAS")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print_success("¡Todas las pruebas pasaron exitosamente!")
    else:
        print_error(f"Fallaron {total - passed} pruebas")
    
    print_section("FIN DE PRUEBAS")

if __name__ == "__main__":
    main() 