# Energy Consumption Prediction API

API para predicción de consumo de energía implementada con arquitectura hexagonal, PostgreSQL y Redis.

## Arquitectura

Este proyecto utiliza **Arquitectura Hexagonal** (también conocida como Ports and Adapters) que proporciona:

- **Separación clara de responsabilidades**
- **Independencia de frameworks**
- **Testabilidad mejorada**
- **Flexibilidad para cambiar tecnologías**

### Estructura del Proyecto

```
app/
├── domain/                 # Capa de dominio (núcleo de negocio)
│   ├── entities/          # Entidades de dominio
│   ├── repositories/      # Interfaces de repositorios
│   └── services/          # Servicios de dominio
├── application/           # Capa de aplicación
│   └── services/          # Servicios de aplicación
├── infrastructure/        # Capa de infraestructura
│   ├── database/          # Modelos de base de datos
│   └── repositories/      # Implementaciones de repositorios
├── api/                   # Capa de presentación
│   └── v1/               # Controladores de API
└── config/               # Configuración
```

## Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache para predicciones
- **SQLAlchemy**: ORM para PostgreSQL
- **Alembic**: Migraciones de base de datos
- **Docker**: Contenerización
- **Docker Compose**: Orquestación de servicios

## Características

- ✅ **Arquitectura Hexagonal**
- ✅ **Cache con Redis** para predicciones
- ✅ **Base de datos PostgreSQL**
- ✅ **Contenerización con Docker**
- ✅ **Autenticación JWT**
- ✅ **Migraciones automáticas**
- ✅ **API RESTful**

## Instalación y Uso

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd energy-consumption-prediction-backend
```

### 2. Configurar variables de entorno

Copia el archivo de configuración de ejemplo:

```bash
cp config.example .env
```

Edita el archivo `.env` con tus configuraciones:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/energy_prediction
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
```

### 3. Ejecutar con Docker Compose

```bash
# Construir y levantar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build
```

### 4. Ejecutar migraciones

```bash
# Ejecutar migraciones
docker-compose exec app alembic upgrade head
```

### 5. Acceder a la API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Endpoints

### Autenticación

- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/token` - Obtener token de acceso
- `GET /auth/me` - Obtener información del usuario actual

### Predicciones

- `POST /predictions/` - Crear nueva predicción
- `GET /predictions/user/{user_id}` - Obtener predicciones de un usuario
- `GET /predictions/date-range/` - Obtener predicciones por rango de fechas
- `DELETE /predictions/user/{user_id}/cache` - Limpiar cache de un usuario

## Desarrollo

### Estructura de la Arquitectura Hexagonal

#### Dominio (Domain)
- **Entidades**: Objetos de negocio puros
- **Repositorios**: Interfaces para acceso a datos
- **Servicios**: Lógica de negocio

#### Aplicación (Application)
- **Servicios**: Orquestación de casos de uso
- **DTOs**: Objetos de transferencia de datos

#### Infraestructura (Infrastructure)
- **Repositorios**: Implementaciones concretas
- **Modelos de BD**: Mapeo a base de datos
- **Configuración**: Conexiones y configuraciones

#### API (Presentation)
- **Controladores**: Endpoints de la API
- **Middlewares**: Autenticación, CORS, etc.

### Cache con Redis

El sistema utiliza Redis para cachear predicciones:

- **Clave de cache**: `prediction:{user_id}:{target_date}`
- **TTL**: 24 horas
- **Beneficios**: 
  - Respuestas más rápidas para predicciones repetidas
  - Reducción de carga en el modelo ML
  - Mejor experiencia de usuario

### Base de Datos

PostgreSQL se utiliza para almacenar:

- **Usuarios**: Información de autenticación
- **Predicciones**: Historial de predicciones generadas
- **Relaciones**: Usuario -> Predicciones

## Comandos Útiles

```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs app

# Ejecutar comandos dentro del contenedor
docker-compose exec app python -c "print('Hello from container')"

# Reiniciar un servicio específico
docker-compose restart app

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v
```

## Migraciones

```bash
# Crear nueva migración
docker-compose exec app alembic revision --autogenerate -m "Description"

# Ejecutar migraciones pendientes
docker-compose exec app alembic upgrade head

# Revertir última migración
docker-compose exec app alembic downgrade -1
```

## Testing

```bash
# Ejecutar tests (cuando estén implementados)
docker-compose exec app python -m pytest
```

## Producción

Para despliegue en producción:

1. Cambiar `SECRET_KEY` por una clave segura
2. Configurar `DATABASE_URL` y `REDIS_URL` para producción
3. Establecer `DEBUG=False`
4. Configurar HTTPS
5. Implementar monitoreo y logging

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.