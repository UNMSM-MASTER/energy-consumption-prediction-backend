# Diagrama Visual de la Arquitectura Hexagonal

## Vista General de la Arquitectura

```mermaid
graph TB
    subgraph "🌐 Adaptadores de Entrada (Driving Adapters)"
        API[API Controllers<br/>FastAPI]
        CLI[CLI Commands]
        WEB[Web Interface]
    end
    
    subgraph "🔧 Capa de Aplicación"
        UC[Use Cases<br/>PredictionUseCases<br/>AuthUseCases]
        AS[Application Services]
    end
    
    subgraph "🎯 Dominio (Core Business)"
        E[Entities<br/>Prediction<br/>User]
        DS[Domain Services<br/>PredictionService]
        R[Repository Interfaces<br/>PredictionRepository<br/>UserRepository<br/>CacheRepository]
    end
    
    subgraph "🏗️ Adaptadores de Salida (Driven Adapters)"
        DB[Database<br/>PostgreSQL]
        CACHE[Cache<br/>Redis]
        ML[ML Models<br/>Scikit-learn]
        AUTH[Auth Service<br/>JWT]
    end
    
    API --> UC
    CLI --> UC
    WEB --> UC
    
    UC --> E
    UC --> DS
    UC --> R
    
    R --> DB
    R --> CACHE
    DS --> ML
    DS --> AUTH
    
    style E fill:#e1f5fe
    style DS fill:#e1f5fe
    style R fill:#e1f5fe
    style UC fill:#f3e5f5
    style API fill:#e8f5e8
    style DB fill:#fff3e0
    style CACHE fill:#fff3e0
    style ML fill:#fff3e0
```

## Flujo Detallado de Predicción

```mermaid
sequenceDiagram
    participant Client
    participant API as API Controller
    participant UC as Use Cases
    participant Domain as Domain Services
    participant Repo as Repository
    participant DB as PostgreSQL
    participant Cache as Redis
    participant ML as ML Models

    Client->>API: POST /prediction/predict
    Note over API: Validación de entrada<br/>Autenticación JWT
    
    API->>UC: make_prediction(input_data, username)
    
    UC->>Cache: get_cached_prediction(cache_key)
    
    alt Cache Hit
        Cache-->>UC: cached_result
        UC-->>API: PredictionResult
    else Cache Miss
        UC->>Domain: load_model(company)
        Domain->>ML: load_model_from_disk()
        ML-->>Domain: model_object
        
        UC->>Domain: get_forecast_lags(company, model, date)
        Domain->>ML: calculate_lags()
        ML-->>Domain: [lag1, lag2, lag3]
        
        UC->>Domain: prepare_features(date, lags)
        Domain-->>UC: feature_vector
        
        UC->>Domain: make_prediction(model, features)
        Domain->>ML: predict(features)
        ML-->>Domain: prediction_value
        
        UC->>Repo: create(prediction_data)
        Repo->>DB: INSERT INTO predictions
        DB-->>Repo: prediction_id
        Repo-->>UC: PredictionResult
        
        UC->>Cache: cache_prediction(result, expire=3600)
        Cache-->>UC: success
        
        UC-->>API: PredictionResult
    end
    
    API-->>Client: JSON Response
```

## Estructura de Dependencias

```mermaid
graph LR
    subgraph "Dependencias Externas"
        FASTAPI[FastAPI]
        SQLALCHEMY[SQLAlchemy]
        REDIS[Redis]
        PANDAS[Pandas]
        SKLEARN[Scikit-learn]
    end
    
    subgraph "Infraestructura"
        INFRA[Infrastructure Layer]
    end
    
    subgraph "Aplicación"
        APP[Application Layer]
    end
    
    subgraph "Dominio"
        DOMAIN[Domain Layer]
    end
    
    subgraph "API"
        API[API Layer]
    end
    
    API --> FASTAPI
    INFRA --> SQLALCHEMY
    INFRA --> REDIS
    INFRA --> PANDAS
    INFRA --> SKLEARN
    
    API --> APP
    APP --> DOMAIN
    INFRA --> DOMAIN
    
    style DOMAIN fill:#e1f5fe
    style APP fill:#f3e5f5
    style INFRA fill:#fff3e0
    style API fill:#e8f5e8
```

## Patrones de Diseño Aplicados

```mermaid
graph TB
    subgraph "Repository Pattern"
        R1[Repository Interface]
        R2[PostgreSQL Implementation]
        R3[Redis Implementation]
        R1 -.->|implements| R2
        R1 -.->|implements| R3
    end
    
    subgraph "Dependency Injection"
        DI1[Use Cases]
        DI2[Repository Interface]
        DI3[Service Interface]
        DI1 --> DI2
        DI1 --> DI3
    end
    
    subgraph "Strategy Pattern"
        S1[Prediction Service Interface]
        S2[ML Strategy 1]
        S3[ML Strategy 2]
        S1 -.->|implements| S2
        S1 -.->|implements| S3
    end
    
    subgraph "Factory Pattern"
        F1[Model Factory]
        F2[Company A Model]
        F3[Company B Model]
        F1 --> F2
        F1 --> F3
    end
    
    style R1 fill:#e1f5fe
    style DI1 fill:#f3e5f5
    style S1 fill:#e1f5fe
    style F1 fill:#fff3e0
```

## Capas y Responsabilidades

```mermaid
graph TB
    subgraph "🌐 API Layer (Adaptadores de Entrada)"
        API1[HTTP Controllers]
        API2[Request/Response DTOs]
        API3[Validation]
        API4[Authentication]
    end
    
    subgraph "🔧 Application Layer (Casos de Uso)"
        APP1[Use Cases]
        APP2[Application Services]
        APP3[Transaction Management]
        APP4[Orchestration]
    end
    
    subgraph "🎯 Domain Layer (Núcleo de Negocio)"
        DOM1[Entities]
        DOM2[Domain Services]
        DOM3[Repository Interfaces]
        DOM4[Business Rules]
    end
    
    subgraph "🏗️ Infrastructure Layer (Adaptadores de Salida)"
        INF1[Database Repositories]
        INF2[External Services]
        INF3[ML Models]
        INF4[Cache Implementation]
    end
    
    API1 --> APP1
    API2 --> APP1
    API3 --> APP1
    API4 --> APP1
    
    APP1 --> DOM1
    APP1 --> DOM2
    APP1 --> DOM3
    APP2 --> DOM1
    
    DOM3 --> INF1
    DOM2 --> INF2
    DOM2 --> INF3
    DOM3 --> INF4
    
    style DOM1 fill:#e1f5fe
    style DOM2 fill:#e1f5fe
    style DOM3 fill:#e1f5fe
    style DOM4 fill:#e1f5fe
    style APP1 fill:#f3e5f5
    style APP2 fill:#f3e5f5
    style APP3 fill:#f3e5f5
    style APP4 fill:#f3e5f5
    style API1 fill:#e8f5e8
    style API2 fill:#e8f5e8
    style API3 fill:#e8f5e8
    style API4 fill:#e8f5e8
    style INF1 fill:#fff3e0
    style INF2 fill:#fff3e0
    style INF3 fill:#fff3e0
    style INF4 fill:#fff3e0
```

## Ventajas de la Arquitectura

```mermaid
mindmap
  root((Arquitectura<br/>Hexagonal))
    Mantenibilidad
      Código organizado
      Cambios localizados
      Refactoring seguro
    Testabilidad
      Tests unitarios
      Mocks fáciles
      Independencia
    Flexibilidad
      Cambio de tecnologías
      Nuevas funcionalidades
      Múltiples interfaces
    Escalabilidad
      Separación clara
      Paralelización
      Microservicios ready
    Seguridad
      Validación múltiple
      Autenticación centralizada
      Autorización granular
```

## Tecnologías por Capa

```mermaid
graph LR
    subgraph "🌐 API Layer"
        FASTAPI[FastAPI]
        PYDANTIC[Pydantic]
        JWT[JWT Auth]
    end
    
    subgraph "🔧 Application Layer"
        ASYNC[Async/Await]
        DI[Dependency Injection]
        UC[Use Cases]
    end
    
    subgraph "🎯 Domain Layer"
        ABC[Abstract Classes]
        ENTITIES[Pydantic Entities]
        INTERFACES[Repository Interfaces]
    end
    
    subgraph "🏗️ Infrastructure Layer"
        SQLALCHEMY[SQLAlchemy]
        REDIS[Redis]
        PANDAS[Pandas]
        SKLEARN[Scikit-learn]
        ALEMBIC[Alembic]
    end
    
    style FASTAPI fill:#e8f5e8
    style PYDANTIC fill:#e8f5e8
    style JWT fill:#e8f5e8
    style ASYNC fill:#f3e5f5
    style DI fill:#f3e5f5
    style UC fill:#f3e5f5
    style ABC fill:#e1f5fe
    style ENTITIES fill:#e1f5fe
    style INTERFACES fill:#e1f5fe
    style SQLALCHEMY fill:#fff3e0
    style REDIS fill:#fff3e0
    style PANDAS fill:#fff3e0
    style SKLEARN fill:#fff3e0
    style ALEMBIC fill:#fff3e0
``` 