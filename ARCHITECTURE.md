# Arquitectura Hexagonal - Energy Consumption Prediction Backend

## Resumen Ejecutivo

Este proyecto implementa una **Arquitectura Hexagonal (Clean Architecture)** para un sistema de predicción de consumo energético. La arquitectura está diseñada para mantener la separación de responsabilidades, facilitar el testing y permitir la evolución independiente de cada capa.

## Estructura de la Arquitectura

```
energy-consumption-prediction-backend/
├── app/
│   ├── domain/           # 🎯 Núcleo de Negocio (Dominio)
│   ├── application/      # 🔧 Casos de Uso (Aplicación)
│   ├── infrastructure/   # 🏗️ Adaptadores Externos (Infraestructura)
│   ├── api/             # 🌐 Adaptadores de Entrada (API)
│   ├── config/          # ⚙️ Configuración
│   ├── middleware/      # 🔄 Middleware
│   ├── utils/           # 🛠️ Utilidades
│   └── db_models/       # 📊 Modelos de Base de Datos
├── main.py              # 🚀 Punto de Entrada
└── requirements.txt     # 📦 Dependencias
```

## Capas de la Arquitectura

### 1. 🎯 Capa de Dominio (`app/domain/`)

**Propósito**: Contiene las reglas de negocio centrales y entidades del dominio.

#### Entidades (`entities/`)
- **`prediction.py`**: Define las entidades del dominio para predicciones
  - `PredictionInput`: Datos de entrada para predicciones
  - `PredictionResult`: Resultado de una predicción
  - `PredictionCreate`: Datos para crear una predicción
- **`user.py`**: Entidades relacionadas con usuarios

#### Repositorios (`repositories/`)
- **`prediction_repository.py`**: Interfaz abstracta para operaciones de predicciones
- **`user_repository.py`**: Interfaz abstracta para operaciones de usuarios
- **`cache_repository.py`**: Interfaz abstracta para operaciones de cache

#### Servicios (`services/`)
- **`prediction_service.py`**: Interfaz abstracta para servicios de predicción ML
- **`auth_service.py`**: Interfaz abstracta para servicios de autenticación

**Características**:
- ✅ No depende de frameworks externos
- ✅ Contiene solo lógica de negocio
- ✅ Define contratos (interfaces) para adaptadores

### 2. 🔧 Capa de Aplicación (`app/application/`)

**Propósito**: Orquesta los casos de uso y coordina entre el dominio y la infraestructura.

#### Casos de Uso (`use_cases/`)
- **`prediction_use_cases.py`**: Implementa la lógica de casos de uso para predicciones
  - `make_prediction()`: Realiza predicciones con cache y persistencia
  - `get_user_predictions()`: Obtiene predicciones de un usuario
  - `get_prediction_by_id()`: Obtiene una predicción específica
  - `preload_model_if_needed()`: Precarga modelos ML en background

- **`auth_use_cases.py`**: Casos de uso para autenticación

#### Servicios (`services/`)
- Servicios de aplicación que coordinan múltiples repositorios

**Características**:
- ✅ Implementa casos de uso específicos
- ✅ Orquesta entidades del dominio
- ✅ Maneja transacciones y coordinación
- ✅ No contiene lógica de negocio

### 3. 🏗️ Capa de Infraestructura (`app/infrastructure/`)

**Propósito**: Implementa los adaptadores externos y proporciona acceso a recursos externos.

#### Repositorios (`repositories/`)
- **`prediction_repository_impl.py`**: Implementación PostgreSQL del repositorio de predicciones
- **`user_repository_impl.py`**: Implementación PostgreSQL del repositorio de usuarios
- **`cache_repository_impl.py`**: Implementación Redis del repositorio de cache

#### Servicios (`services/`)
- **`prediction_service_impl.py`**: Implementación concreta del servicio de predicción ML

#### Base de Datos (`database/`)
- Configuración y modelos de base de datos
- Migraciones con Alembic

**Características**:
- ✅ Implementa interfaces del dominio
- ✅ Maneja detalles técnicos (PostgreSQL, Redis, ML)
- ✅ Es intercambiable sin afectar el dominio

### 4. 🌐 Capa de API (`app/api/`)

**Propósito**: Expone la funcionalidad a través de endpoints HTTP.

#### Controladores (`v1/prediction/`)
- **`prediction_controller.py`**: Endpoints para predicciones
  - `POST /prediction/predict`: Realizar predicción
  - `GET /prediction/predictions`: Obtener predicciones del usuario
  - `GET /prediction/predictions/{id}`: Obtener predicción específica

- **`cache_controller.py`**: Endpoints para gestión de cache

#### Autenticación (`v1/auth/`)
- **`auth_controller.py`**: Endpoints de autenticación
- **`jwt_auth.py`**: Middleware de autenticación JWT

**Características**:
- ✅ Adaptador de entrada (driving adapter)
- ✅ Maneja HTTP, serialización, validación
- ✅ Inyecta dependencias usando FastAPI

## Flujo de Datos

### 1. Flujo de Predicción

```mermaid
sequenceDiagram
    participant Client
    participant API as API Controller
    participant UC as Use Cases
    participant Domain as Domain Services
    participant Repo as Repository
    participant DB as Database
    participant Cache as Redis Cache
    participant ML as ML Models

    Client->>API: POST /prediction/predict
    API->>UC: make_prediction(input_data, username)
    UC->>Cache: get_cached_prediction(cache_key)
    alt Cache Hit
        Cache-->>UC: cached_result
        UC-->>API: PredictionResult
    else Cache Miss
        UC->>Domain: load_model(company)
        Domain->>ML: load_model_from_disk
        UC->>Domain: get_forecast_lags(company, model, date)
        Domain->>ML: calculate_lags
        UC->>Domain: prepare_features(date, lags)
        UC->>Domain: make_prediction(model, features)
        Domain->>ML: predict
        UC->>Repo: create(prediction)
        Repo->>DB: INSERT prediction
        UC->>Cache: cache_prediction(result)
        UC-->>API: PredictionResult
    end
    API-->>Client: JSON Response
```

### 2. Inyección de Dependencias

```python
# En prediction_controller.py
def get_prediction_use_cases(db=Depends(get_db)) -> PredictionUseCases:
    prediction_repository = PostgreSQLPredictionRepository(db)
    cache_repository = RedisCacheRepository()
    prediction_service = MLPredictionService(cache_repository)
    return PredictionUseCases(prediction_repository, cache_repository, prediction_service)
```

## Principios de Diseño Aplicados

### 1. 🔄 Inversión de Dependencias
- El dominio define interfaces (abstracciones)
- La infraestructura implementa esas interfaces
- La aplicación depende de abstracciones, no de implementaciones

### 2. 🎯 Separación de Responsabilidades
- **Dominio**: Reglas de negocio puras
- **Aplicación**: Casos de uso y orquestación
- **Infraestructura**: Acceso a recursos externos
- **API**: Presentación y comunicación

### 3. 🔌 Adaptadores Intercambiables
- Repositorios pueden cambiar de PostgreSQL a MongoDB
- Cache puede cambiar de Redis a Memcached
- Servicios ML pueden cambiar de implementación

### 4. 🧪 Testabilidad
- Cada capa puede ser testeada independientemente
- Fácil mock de dependencias
- Tests unitarios sin dependencias externas

## Tecnologías y Herramientas

### Backend Framework
- **FastAPI**: Framework web moderno con soporte nativo para async/await
- **Pydantic**: Validación de datos y serialización
- **SQLAlchemy**: ORM para PostgreSQL

### Machine Learning
- **Scikit-learn**: Modelos de predicción
- **Pandas**: Manipulación de datos
- **NumPy**: Computación numérica

### Infraestructura
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y sesiones
- **Docker**: Containerización
- **Nginx**: Proxy reverso

### Monitoreo y Logging
- **Structured Logging**: Logs estructurados
- **Health Checks**: Endpoints de salud
- **Timeout Management**: Manejo de timeouts

## Configuración y Despliegue

### Variables de Entorno
```bash
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
MODEL_PATH=/app/ml_models
```

### Docker Compose
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:13
    
  redis:
    image: redis:6
```

## Ventajas de esta Arquitectura

### 1. 🚀 Mantenibilidad
- Código organizado y fácil de navegar
- Cambios localizados en capas específicas
- Refactoring seguro

### 2. 🔄 Flexibilidad
- Fácil cambio de tecnologías
- Nuevas funcionalidades sin afectar existentes
- Múltiples interfaces (REST, GraphQL, gRPC)

### 3. 🧪 Testabilidad
- Tests unitarios independientes
- Mocks fáciles de implementar
- Cobertura de código alta

### 4. 📈 Escalabilidad
- Separación clara de responsabilidades
- Fácil paralelización de desarrollo
- Microservicios ready

### 5. 🔒 Seguridad
- Validación en múltiples capas
- Autenticación centralizada
- Autorización granular

## Patrones de Diseño Utilizados

1. **Repository Pattern**: Abstracción del acceso a datos
2. **Dependency Injection**: Inversión de control
3. **Use Case Pattern**: Casos de uso específicos
4. **Adapter Pattern**: Adaptadores para tecnologías externas
5. **Factory Pattern**: Creación de objetos complejos
6. **Strategy Pattern**: Diferentes algoritmos de ML

## Métricas y Monitoreo

### Health Checks
- `/health`: Estado básico del servicio
- `/health/detailed`: Estado detallado de componentes

### Logging
- Logs estructurados en formato JSON
- Niveles de log configurables
- Trazabilidad de requests

### Timeouts
- Nginx: 900s
- FastAPI: 900s
- Predicciones: 720s
- Carga de modelos: 300s

## Conclusión

Esta implementación de Arquitectura Hexagonal proporciona:

- ✅ **Separación clara** de responsabilidades
- ✅ **Independencia** de frameworks externos
- ✅ **Testabilidad** mejorada
- ✅ **Mantenibilidad** a largo plazo
- ✅ **Escalabilidad** para futuras necesidades
- ✅ **Flexibilidad** para cambios tecnológicos

La arquitectura está diseñada para evolucionar con el negocio mientras mantiene la estabilidad y calidad del código. 