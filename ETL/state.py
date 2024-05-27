import abc
import json
from typing import Any, Optional


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def retrieve_state(self):
        try:
            with open(self.file_path, "r") as f:
                state = json.load(f)
        except FileNotFoundError:
            state = {}
        return state

    def save_state(self, state: dict):
        with open(self.file_path, "w") as f:
            json.dump(state, f)


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.dict_ = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.dict_[key] = value
        self.storage.save_state(self.dict_)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.dict_.get(key, None)
