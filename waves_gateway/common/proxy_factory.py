"""ProxyFactory"""

from typing import Callable


class ProxyFactory(object):
    """
    Create a new instance (using the provided factory) for every attribute request.
    """

    def __init__(self, factory: Callable) -> None:
        self._factory = factory

    def __getattr__(self, item):
        return getattr(self._factory(), item)
