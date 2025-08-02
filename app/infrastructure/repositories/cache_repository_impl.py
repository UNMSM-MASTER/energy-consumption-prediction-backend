from typing import Optional, Any, Dict
import json
import redis.asyncio as redis
from app.domain.repositories.cache_repository import CacheRepository
from app.config.settings import get_settings
from app.utils.logger import logger
from app.utils.exceptions import CacheException

settings = get_settings()


class RedisCacheRepository(CacheRepository):
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info(
                "Redis cache repository initialized",
                extra_fields={
                    "redis_url": settings.REDIS_URL.replace(settings.REDIS_URL.split('@')[0].split(':')[-1], '***') if '@' in settings.REDIS_URL else settings.REDIS_URL,
                    "operation": "initialize"
                }
            )
        except Exception as e:
            logger.error(
                "Failed to initialize Redis cache repository",
                extra_fields={
                    "redis_url": settings.REDIS_URL,
                    "operation": "initialize",
                    "error": str(e)
                },
                exc_info=True
            )
            raise CacheException(
                f"Error inicializando Redis: {str(e)}",
                details={"redis_url": settings.REDIS_URL}
            )

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            
            await self.redis_client.set(key, value, ex=expire)
            
            logger.debug(
                "Cache set operation successful",
                extra_fields={
                    "key": key,
                    "expire_seconds": expire,
                    "operation": "set"
                }
            )
            return True
        except Exception as e:
            logger.error(
                "Cache set operation failed",
                extra_fields={
                    "key": key,
                    "expire_seconds": expire,
                    "operation": "set",
                    "error": str(e)
                },
                exc_info=True
            )
            raise CacheException(
                f"Error setting cache key {key}: {str(e)}",
                details={"key": key, "expire_seconds": expire}
            )

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis_client.get(key)
            if value is None:
                logger.debug(
                    "Cache miss",
                    extra_fields={
                        "key": key,
                        "operation": "get"
                    }
                )
                return None
            
            try:
                parsed_value = json.loads(value)
                logger.debug(
                    "Cache hit (JSON)",
                    extra_fields={
                        "key": key,
                        "operation": "get"
                    }
                )
                return parsed_value
            except json.JSONDecodeError:
                logger.debug(
                    "Cache hit (string)",
                    extra_fields={
                        "key": key,
                        "operation": "get"
                    }
                )
                return value
        except Exception as e:
            logger.error(
                "Cache get operation failed",
                extra_fields={
                    "key": key,
                    "operation": "get",
                    "error": str(e)
                },
                exc_info=True
            )
            raise CacheException(
                f"Error getting cache key {key}: {str(e)}",
                details={"key": key}
            )

    async def delete(self, key: str) -> bool:
        try:
            result = await self.redis_client.delete(key)
            success = result > 0
            
            logger.debug(
                "Cache delete operation completed",
                extra_fields={
                    "key": key,
                    "success": success,
                    "operation": "delete"
                }
            )
            return success
        except Exception as e:
            logger.error(
                "Cache delete operation failed",
                extra_fields={
                    "key": key,
                    "operation": "delete",
                    "error": str(e)
                },
                exc_info=True
            )
            raise CacheException(
                f"Error deleting cache key {key}: {str(e)}",
                details={"key": key}
            )

    async def exists(self, key: str) -> bool:
        try:
            result = await self.redis_client.exists(key) > 0
            
            logger.debug(
                "Cache exists check completed",
                extra_fields={
                    "key": key,
                    "exists": result,
                    "operation": "exists"
                }
            )
            return result
        except Exception as e:
            logger.error(
                "Cache exists check failed",
                extra_fields={
                    "key": key,
                    "operation": "exists",
                    "error": str(e)
                },
                exc_info=True
            )
            raise CacheException(
                f"Error checking cache key {key}: {str(e)}",
                details={"key": key}
            )

    async def set_hash(self, key: str, mapping: Dict[str, Any], expire: int = 3600) -> bool:
        try:
            # Serializar valores que no son strings
            serialized_mapping = {}
            for field, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized_mapping[field] = json.dumps(value, default=str)
                else:
                    serialized_mapping[field] = str(value)
            
            await self.redis_client.hset(key, mapping=serialized_mapping)
            await self.redis_client.expire(key, expire)
            
            logger.debug(
                "Cache hash set operation successful",
                extra_fields={
                    "key": key,
                    "fields_count": len(mapping),
                    "expire_seconds": expire,
                    "operation": "set_hash"
                }
            )
            return True
        except Exception as e:
            logger.error(
                "Cache hash set operation failed",
                extra_fields={
                    "key": key,
                    "fields_count": len(mapping),
                    "expire_seconds": expire,
                    "operation": "set_hash",
                    "error": str(e)
                },
                exc_info=True
            )
            raise CacheException(
                f"Error setting cache hash {key}: {str(e)}",
                details={"key": key, "fields_count": len(mapping)}
            )

    async def get_hash(self, key: str, field: str) -> Optional[Any]:
        try:
            value = await self.redis_client.hget(key, field)
            if value is None:
                logger.debug(
                    "Cache hash field miss",
                    extra_fields={
                        "key": key,
                        "field": field,
                        "operation": "get_hash"
                    }
                )
                return None
            
            try:
                parsed_value = json.loads(value)
                logger.debug(
                    "Cache hash field hit (JSON)",
                    extra_fields={
                        "key": key,
                        "field": field,
                        "operation": "get_hash"
                    }
                )
                return parsed_value
            except json.JSONDecodeError:
                logger.debug(
                    "Cache hash field hit (string)",
                    extra_fields={
                        "key": key,
                        "field": field,
                        "operation": "get_hash"
                    }
                )
                return value
        except Exception as e:
            logger.error(
                "Cache hash get operation failed",
                extra_fields={
                    "key": key,
                    "field": field,
                    "operation": "get_hash",
                    "error": str(e)
                },
                exc_info=True
            )
            raise CacheException(
                f"Error getting cache hash field {key}:{field}: {str(e)}",
                details={"key": key, "field": field}
            )

    async def get_all_hash(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            hash_data = await self.redis_client.hgetall(key)
            if not hash_data:
                logger.debug(
                    "Cache hash miss (empty)",
                    extra_fields={
                        "key": key,
                        "operation": "get_all_hash"
                    }
                )
                return None
            
            result = {}
            for field, value in hash_data.items():
                try:
                    result[field] = json.loads(value)
                except json.JSONDecodeError:
                    result[field] = value
            
            logger.debug(
                "Cache hash hit",
                extra_fields={
                    "key": key,
                    "fields_count": len(result),
                    "operation": "get_all_hash"
                }
            )
            return result
        except Exception as e:
            logger.error(
                "Cache hash get all operation failed",
                extra_fields={
                    "key": key,
                    "operation": "get_all_hash",
                    "error": str(e)
                },
                exc_info=True
            )
            raise CacheException(
                f"Error getting all cache hash {key}: {str(e)}",
                details={"key": key}
            ) 