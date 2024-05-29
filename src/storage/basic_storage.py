from abc import ABC, abstractmethod


class AsyncStorage(ABC):
    @abstractmethod
    async def get(self, object_id: str, **kwargs):
        pass

    @abstractmethod
    async def get_all(self, **kwargs):
        pass
