"""
ProxyGuard
"""

from typing import Optional, Any
from gevent.lock import Semaphore


class ProxyGuard(object):
    """
    Helper class that can be used to protect an proxy object that represents a remote resource.
    It is possible to specify the maximum number of parallel calls of any method.
    This is helpful in the case that the resource limits the number of parallel connections.
    """

    def __init__(self,
                 proxy: Any,
                 max_parallel_access=1,
                 attr_name: Optional[str] = None,
                 semaphore: Optional[Semaphore] = None) -> None:
        self._attr_name = attr_name
        self._proxy = proxy
        self._max_parallel_access = max_parallel_access

        if semaphore is not None:
            self._semaphore = semaphore
        else:
            self._semaphore = Semaphore(value=max_parallel_access)

    def __getattr__(self, name):
        return ProxyGuard(
            self._proxy, max_parallel_access=self._max_parallel_access, attr_name=name, semaphore=self._semaphore)

    def __call__(self, *args, **kwargs) -> Any:
        self._semaphore.acquire(blocking=True)

        ex = None
        result = None

        try:
            result = getattr(self._proxy, self._attr_name)(*args, **kwargs)
        except BaseException as base_exception:
            ex = base_exception
        finally:
            self._semaphore.release()

        if ex is not None:
            raise ex

        return result
