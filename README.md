# 🔋 Energy Consumption Prediction Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-CC0000?style=for-the-badge&logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-3.8-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

Sistema de predicción de consumo energético desarrollado con **Arquitectura Hexagonal (Clean Architecture)** para Osinergmin. El proyecto proporciona APIs robustas para autenticación de usuarios y predicciones de consumo energético utilizando modelos de Machine Learning.

## 🏗️ Arquitectura

Este proyecto implementa una **Arquitectura Hexagonal** que separa claramente las responsabilidades en capas:

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 API Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Auth API      │  │ Prediction API  │  │  Cache API   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  🔧 Application Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Prediction UC   │  │   Auth UC       │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    🎯 Domain Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Entities      │  │  Repositories   │  │   Services   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                🏗️ Infrastructure Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   PostgreSQL    │  │     Redis       │  │  ML Models   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Capas Principales

- **🎯 Domain Layer**: Entidades de negocio, repositorios abstractos y servicios del dominio
- **🔧 Application Layer**: Casos de uso que orquestan la lógica de negocio
- **🌐 API Layer**: Controladores REST que exponen la funcionalidad
- **🏗️ Infrastructure Layer**: Implementaciones concretas (PostgreSQL, Redis, ML Models)

## ✨ Características Principales

### 🔐 Autenticación y Autorización
- Sistema de autenticación JWT
- Registro y login de usuarios
- Gestión de tokens con expiración configurable
- Integración con Firebase para almacenamiento seguro

### 🤖 Predicciones de Machine Learning
- Modelos de Random Forest para predicción de consumo energético
- Carga dinámica de modelos desde Firebase Storage
- Sistema de cache con Redis para optimizar rendimiento
- Predicciones en tiempo real con validación de datos

### 🗄️ Persistencia de Datos
- Base de datos PostgreSQL para datos persistentes
- Cache Redis para optimización de consultas
- Migraciones automáticas con Alembic
- Modelos SQLAlchemy con validación Pydantic

### 📊 Monitoreo y Logging
- Sistema de logging estructurado
- Middleware de logging automático
- Health checks para monitoreo
- Manejo global de excepciones

### 🚀 Escalabilidad
- Arquitectura hexagonal para fácil mantenimiento
- Separación de responsabilidades
- Inyección de dependencias
- Testing unitario facilitado

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para PostgreSQL
- **Pydantic**: Validación de datos y serialización
- **Alembic**: Migraciones de base de datos

### Machine Learning
- **Scikit-learn**: Modelos de Random Forest
- **Joblib**: Serialización de modelos
- **Pandas**: Manipulación de datos

### Infraestructura
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y sesiones
- **Docker & Docker Compose**: Containerización
- **Firebase Storage**: Almacenamiento de modelos ML

### Autenticación
- **JWT**: Tokens de autenticación
- **Firebase Admin**: Integración con servicios de Google
- **Passlib**: Hashing de contraseñas

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Docker y Docker Compose
- Cuenta de Firebase (para almacenamiento de modelos)

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd energy-consumption-prediction-backend
```

### 2. Configurar Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/energy_prediction

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Models
MODELS_PATH=/app/ml_models

# Firebase Configuration
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
FIREBASE_UNIVERSE_DOMAIN=googleapis.com
```

### 3. Ejecutar con Docker Compose
```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build
```

### 4. Instalación Local (Alternativa)
```bash
# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos PostgreSQL y Redis
# Ejecutar migraciones
alembic upgrade head

# Iniciar aplicación
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 Uso de la API

### Documentación Interactiva
Una vez ejecutada la aplicación, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### 🔐 Autenticación
```http
POST /auth/register
POST /auth/login
POST /auth/refresh
```

#### 🤖 Predicciones
```http
POST /prediction/predict
GET /prediction/user/{user_id}
GET /prediction/{prediction_id}
```

#### 💾 Cache
```http
GET /cache/status
POST /cache/clear
```

### Ejemplo de Uso

#### 1. Registrar Usuario
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "password123",
    "full_name": "Usuario Ejemplo"
  }'
```

#### 2. Realizar Predicción
```bash
curl -X POST "http://localhost:8000/prediction/predict" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "ENERGY_CONSUMPTION",
    "features": {
      "temperature": 25.5,
      "humidity": 60.0,
      "hour": 14,
      "day_of_week": 1
    }
  }'
```

## 🧪 Testing

```bash
# Ejecutar tests unitarios
pytest

# Ejecutar tests con coverage
pytest --cov=app

# Ejecutar tests de integración
pytest tests/integration/
```

## 📊 Monitoreo

### Health Checks
```bash
# Verificar estado de la aplicación
curl http://localhost:8000/health

# Verificar estado del cache
curl http://localhost:8000/cache/status
```

### Logs
Los logs se almacenan en el directorio `logs/` y también se muestran en la consola con formato estructurado.

## 🔧 Desarrollo

### Estructura del Proyecto
```
energy-consumption-prediction-backend/
├── app/
│   ├── api/                    # Controladores REST
│   │   └── v1/
│   │       ├── auth/           # Autenticación
│   │       └── prediction/     # Predicciones
│   ├── application/            # Casos de uso
│   ├── domain/                 # Entidades y repositorios abstractos
│   ├── infrastructure/         # Implementaciones concretas
│   ├── config/                 # Configuración
│   ├── middleware/             # Middleware personalizado
│   ├── utils/                  # Utilidades
│   └── ml_models/              # Modelos de ML
├── alembic/                    # Migraciones de BD
├── logs/                       # Logs de aplicación
├── ml_models/                  # Modelos ML (volumen Docker)
├── main.py                     # Punto de entrada
├── requirements.txt            # Dependencias Python
├── docker-compose.yml          # Orquestación de servicios
└── Dockerfile                  # Imagen Docker
```

### Comandos Útiles

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f app

# Ejecutar migraciones manualmente
docker-compose exec app alembic upgrade head

# Acceder a la base de datos
docker-compose exec postgres psql -U postgres -d energy_prediction

# Acceder a Redis CLI
docker-compose exec redis redis-cli
```

## 🚀 Despliegue

### Producción
Para desplegar en producción:

1. Configurar variables de entorno de producción
2. Usar un reverse proxy (nginx)
3. Configurar SSL/TLS
4. Implementar monitoreo y alertas
5. Configurar backups de base de datos

### Variables de Entorno de Producción
```env
# Configuraciones de producción
DATABASE_URL=postgresql://user:pass@prod-db:5432/energy_prediction
REDIS_URL=redis://prod-redis:6379
SECRET_KEY=your-production-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar la documentación en `/docs`

---

**Desarrollado con ❤️ para Osinergmin**