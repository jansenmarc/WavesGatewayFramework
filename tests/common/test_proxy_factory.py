from unittest import TestCase

from waves_gateway import ProxyFactory


class TestObject(object):
    def test_1(self):
        return id(self)


class ProxyFactoryTest(TestCase):
    def test_proxy_factory(self):
        proxy_factory = ProxyFactory(factory=lambda: TestObject())
        self.assertIsNot(proxy_factory.test_1(), proxy_factory.test_1())
