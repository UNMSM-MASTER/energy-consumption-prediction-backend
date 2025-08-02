from typing import Optional, Any, Dict
import json
import redis.asyncio as redis
from app.domain.repositories.cache_repository import CacheRepository
from app.config.settings import get_settings

settings = get_settings()


class RedisCacheRepository(CacheRepository):
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self.redis_client.set(key, value, ex=expire)
            return True
        except Exception:
            return False

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception:
            return None

    async def delete(self, key: str) -> bool:
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        try:
            return await self.redis_client.exists(key) > 0
        except Exception:
            return False

    async def set_hash(self, key: str, mapping: Dict[str, Any], expire: int = 3600) -> bool:
        try:
            # Serializar valores que no son strings
            serialized_mapping = {}
            for field, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized_mapping[field] = json.dumps(value)
                else:
                    serialized_mapping[field] = str(value)
            
            await self.redis_client.hset(key, mapping=serialized_mapping)
            await self.redis_client.expire(key, expire)
            return True
        except Exception:
            return False

    async def get_hash(self, key: str, field: str) -> Optional[Any]:
        try:
            value = await self.redis_client.hget(key, field)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception:
            return None

    async def get_all_hash(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            hash_data = await self.redis_client.hgetall(key)
            if not hash_data:
                return None
            
            result = {}
            for field, value in hash_data.items():
                try:
                    result[field] = json.loads(value)
                except json.JSONDecodeError:
                    result[field] = value
            return result
        except Exception:
            return None 