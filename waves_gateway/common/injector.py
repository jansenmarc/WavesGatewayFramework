"""
Injector
"""

from typing import List, Any, Dict, Optional, Callable, Union, NewType, Type
from .exceptions import InjectorError
from .utils import map_array


class InjectionToken(object):
    """
    Represents a token that can be used to inject something.
    """

    def __init__(self, name: str, _type: Optional[Any] = None) -> None:
        self._name = name
        self._type = _type

    def __str__(self):
        if self._type is not None:
            return '(' + self._name + ', ' + str(self._type.__name__) + ')'
        else:
            return self._name


Token = Union[Callable, str, InjectionToken]


class DependencyConfiguration(object):
    """
    Configuration for a specific token that is necessary to instantiate the represented class or it may already contain an instance/variable.
    """

    def __init__(self,
                 deps: List[Token] = None,
                 instance: Any = None,
                 factory: Optional[Callable] = None,
                 opt_deps: List[Token] = None,
                 weak: bool = False) -> None:
        if deps is None:
            self._deps = list()  # type: List[Token]
        else:
            self._deps = deps

        if opt_deps is None:
            self._opt_deps = list()  # type: List[Token]
        else:
            self._opt_deps = opt_deps

        self._instance = instance
        self._factory = factory
        self._weak = weak

    @property
    def deps(self) -> List[Token]:
        return self._deps

    @property
    def factory(self) -> Optional[Callable]:
        return self._factory

    @property
    def instance(self) -> Any:
        return self._instance

    @instance.setter
    def instance(self, instance: Any):
        self._instance = instance

    @property
    def opt_deps(self):
        return self._opt_deps

    @property
    def weak(self):
        return self._weak


GLOBAL_DEPENDENCY_MAP = dict()  # type: Dict[Token, DependencyConfiguration]


class Injector(object):
    """
    An injector can be used to retrieve a specific instance or variable by a token.
    It operates on a dependency_map that contains all configuration necessary for the injector to work.
    The root injector uses the global_dependency_map. Any other injector has its own dependency_map and forwards missing tokens to its parent
    injector.
    """

    def __init__(self, dependency_map: Dict[Token, Any]) -> None:
        self._dependency_map = dependency_map

    def provide(self, token: Token, instance: Any, weak=False) -> None:
        if token in self._dependency_map and self._dependency_map[token].weak is False:
            raise InjectorError('Token ' + str(token) + " is already defined and cannot be overwritten.")

        self._dependency_map[token] = DependencyConfiguration(instance=instance, weak=weak)

    def overwrite(self, token: Token, instance: Any) -> None:
        self._dependency_map[token] = DependencyConfiguration(instance=instance)

    def overwrite_if_exists(self, token: Token, instance: Optional[Any]) -> None:
        if instance is not None:
            self.overwrite(token, instance)

    def is_registered(self, token: Token) -> bool:
        """Returns whether the given token is registered in this injector or one of its parents (if any)."""
        return token in self._dependency_map

    def get(self, token: Token) -> Any:
        if not self.is_registered(token):
            raise InjectorError("Cannot provide " + str(token))

        if self._dependency_map[token].instance is not None:
            return self._dependency_map[token].instance

        if self._dependency_map[token].factory is not None:
            self._dependency_map[token].instance = self._dependency_map[token].factory(self)
            return self._dependency_map[token].instance

        try:
            args = map_array(self.get, self._dependency_map[token].deps)
        except InjectorError:
            raise InjectorError('Cannot get all dependencies of ' + str(token))

        def get_opt_dep(token: Token):
            """
            Tries to resolve an dependency and returns None if it has failed.
            """
            try:
                return self.get(token)
            except InjectorError:
                return None

        opt_args = map_array(get_opt_dep, self._dependency_map[token].opt_deps)

        for opt_arg in opt_args:
            args.append(opt_arg)

        if callable(token):
            try:
                self._dependency_map[token].instance = token(*args)
                return self._dependency_map[token].instance
            except InjectorError:
                raise InjectorError('Cannot instantiate ' + str(token))
        else:
            raise InjectorError('Cannot determine how to construct ' + str(token))

    def invoke(self, deps: List[Token], func: Callable, opt_deps: List[Token] = None) -> Any:
        if opt_deps is None:
            opt_deps = list()

        def get_opt_dep(token: Token):
            """Tries to resolve the dependency and returns None of this has failed."""
            try:
                return self.get(token)
            except InjectorError:
                return None

        opt_args = map_array(get_opt_dep, opt_deps)
        args = map_array(self.get, deps)

        for opt_arg in opt_args:
            args.append(opt_arg)

        return func(*args)


INJECTOR = Injector(GLOBAL_DEPENDENCY_MAP)

INJECTOR.provide(Injector, INJECTOR)


class Injectable(object):
    """
    Declares the annotated class to be injectable. It allows to specify a list of dependencies that are injected in the given order.
    The dependencies must be token. In the background this annotation adds an additional token to the global_dependency_map
    making the class usable in any injector instance.
    """

    def __init__(self,
                 provides: Optional[Token] = None,
                 deps: List[Token] = None,
                 dependency_map: Dict[Token, DependencyConfiguration] = GLOBAL_DEPENDENCY_MAP,
                 opt_deps: List[Token] = None,
                 weak: bool = False) -> None:
        if deps is not None:
            self._depends = deps
        else:
            self._depends = list()

        if opt_deps is None:
            self._opt_deps = list()  # type: List[Token]
        else:
            self._opt_deps = opt_deps

        self._token = provides
        self._dependency_map = dependency_map
        self._weak = weak

    def __call__(self, clazz: Type, *args, **kwargs):
        if self._token is not None:
            token = self._token
        else:
            token = clazz

        if token in self._dependency_map and self._dependency_map[token].weak is False:
            raise InjectorError('Token ' + str(token) + " is already defined and cannot be overwritten.")

        self._dependency_map[token] = DependencyConfiguration(
            factory=lambda injector: injector.invoke(self._depends, clazz, self._opt_deps), weak=self._weak)
        return clazz


class Factory(object):
    """
    Declares an annotated function to be a factory for something that is injectable.
    The factory function itself can have dependencies and provides a token.
    """

    def __init__(self,
                 provides: Token,
                 deps: List[Token] = None,
                 opt_deps: List[Token] = None,
                 dependency_map: Dict[Token, DependencyConfiguration] = GLOBAL_DEPENDENCY_MAP,
                 weak: bool = False) -> None:
        if deps is None:
            self._deps = list()  # type: List[Token]
        else:
            self._deps = deps

        if opt_deps is None:
            self._opt_deps = list()  # type: List[Token]
        else:
            self._opt_deps = opt_deps

        self._provides = provides
        self._dependency_map = dependency_map
        self._weak = weak

    def __call__(self, func: Callable, *args, **kwargs):

        if self._provides in self._dependency_map and self._dependency_map[self._provides].weak is False:
            raise InjectorError('Token ' + str(self._provides) + " is already defined and cannot be overwritten.")

        self._dependency_map[self._provides] = DependencyConfiguration(
            factory=lambda injector: injector.invoke(self._deps, func, self._opt_deps), weak=self._weak)

        return func
