"""Serializer"""

from abc import ABC, abstractmethod
from typing import Any


class Serializer(ABC):
    """Base class for all serializers. Ensures a similar API."""

    @abstractmethod
    def as_dict(self, value: Any) -> dict:
        pass

    def from_dict(self, data: dict) -> Any:
        pass
