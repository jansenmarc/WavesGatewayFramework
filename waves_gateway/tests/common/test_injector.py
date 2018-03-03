from typing import Dict, Any
from unittest import TestCase
from waves_gateway.common import Injectable, Injector, Factory, InjectionToken, InjectorError, Token, DependencyConfiguration

test_dependency_map = dict()  # type: Dict[Token, DependencyConfiguration]


@Injectable(dependency_map=test_dependency_map)
class NoDepsClass(object):
    def __init__(self) -> None:
        pass


@Injectable(deps=[NoDepsClass], dependency_map=test_dependency_map)
class ClassWithDeps(object):
    def __init__(self, no_deps_class_instance: NoDepsClass) -> None:
        self.no_deps_class_instance = no_deps_class_instance


other_class_with_deps_token = InjectionToken("class_with_deps", ClassWithDeps)


@Factory(deps=[NoDepsClass], dependency_map=test_dependency_map, provides=other_class_with_deps_token)
def other_class_with_deps_factory(no_deps_class: NoDepsClass):
    return ClassWithDeps(no_deps_class)


class OtherNoDepsClassImpl(object):
    def __init__(self):
        pass


@Injectable(deps=['missing_dep'], dependency_map=test_dependency_map)
class MissingDepsClass(object):
    def __init__(self, missing_dep: str) -> None:
        self.missing_dep = missing_dep


class TestInjector(TestCase):
    def setUp(self):
        self._global_injector = Injector(dependency_map=test_dependency_map)

    def tearDown(self):
        """Clears all created instances."""
        test_dependency_map[NoDepsClass].instance = None
        test_dependency_map[ClassWithDeps].instance = None
        test_dependency_map[other_class_with_deps_token] = None
        test_dependency_map[MissingDepsClass] = None

    def test_inject(self):
        no_deps_class_instance = self._global_injector.get(NoDepsClass)
        class_with_deps_instance = self._global_injector.get(ClassWithDeps)
        other_class_with_deps_instance = self._global_injector.get(other_class_with_deps_token)

        self.assertIsInstance(no_deps_class_instance, NoDepsClass)
        self.assertIsInstance(class_with_deps_instance, ClassWithDeps)
        self.assertIsInstance(other_class_with_deps_instance, ClassWithDeps)
        self.assertIsNot(other_class_with_deps_instance, class_with_deps_instance)
        self.assertIs(other_class_with_deps_instance.no_deps_class_instance, no_deps_class_instance)
        self.assertIs(class_with_deps_instance.no_deps_class_instance, no_deps_class_instance)

        with self.assertRaises(InjectorError):
            self._global_injector.get(MissingDepsClass)

        self._global_injector.overwrite('missing_dep', 'dep')
        missing_deps_instance = self._global_injector.get(MissingDepsClass)  # type: MissingDepsClass
        self.assertIs(missing_deps_instance.missing_dep, 'dep')

    def test_invoke(self):
        def sync_callback(class_with_deps: ClassWithDeps, nothing):
            self.assertIsInstance(class_with_deps, ClassWithDeps)
            self.assertIsNone(nothing)

        self._global_injector.invoke([ClassWithDeps], sync_callback, opt_deps=["nothing"])
