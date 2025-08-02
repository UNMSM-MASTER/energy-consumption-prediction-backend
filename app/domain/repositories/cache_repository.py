from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import json


class CacheRepository(ABC):
    @abstractmethod
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    async def set_hash(self, key: str, mapping: Dict[str, Any], expire: int = 3600) -> bool:
        pass

    @abstractmethod
    async def get_hash(self, key: str, field: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def get_all_hash(self, key: str) -> Optional[Dict[str, Any]]:
        pass 