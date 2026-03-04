from collections import OrderedDict
from typing import Optional


class FileIdCache:
    def __init__(self, max_entries: int = 5000):
        self.max_entries = max_entries
        self._data: OrderedDict[str, str] = OrderedDict()

    def get(self, key: str) -> Optional[str]:
        value = self._data.get(key)
        if value is None:
            return None
        self._data.move_to_end(key)
        return value

    def set(self, key: str, file_id: str) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = file_id
        if len(self._data) > self.max_entries:
            self._data.popitem(last=False)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)
