"""ABSTRACT FACTORY: her fabrika kendi üreticisinin cihaz ailesini üretir."""
from akilli_ev import (DeviceFactory, Light, LumaFactory, LumaLightAdapter,
                       LumaThermostatAdapter, NovaFactory, NovaLightAdapter,
                       NovaThermostatAdapter, Thermostat)
from tests.helpers import QuietTestCase


class FactoryTests(QuietTestCase):
    def test_luma_factory_creates_luma_family(self):
        f = LumaFactory()
        self.assertIsInstance(f.create_light("a"), LumaLightAdapter)
        self.assertIsInstance(f.create_thermostat("b"), LumaThermostatAdapter)

    def test_nova_factory_creates_nova_family(self):
        f = NovaFactory()
        self.assertIsInstance(f.create_light("a"), NovaLightAdapter)
        self.assertIsInstance(f.create_thermostat("b"), NovaThermostatAdapter)

    def test_products_follow_common_interfaces(self):
        for factory in (LumaFactory(), NovaFactory()):
            self.assertIsInstance(factory, DeviceFactory)
            self.assertIsInstance(factory.create_light("x"), Light)
            self.assertIsInstance(factory.create_thermostat("y"), Thermostat)

    def test_same_factory_shares_one_connection(self):
        f = LumaFactory()
        light, thermo = f.create_light("a"), f.create_thermostat("b")
        self.assertIs(light._bridge, thermo._bridge)
        g = NovaFactory()
        self.assertIs(g.create_light("a")._cloud, g.create_thermostat("b")._cloud)

    def test_different_factories_do_not_share_connection(self):
        self.assertIsNot(LumaFactory().create_light("a")._bridge,
                         LumaFactory().create_light("a")._bridge)

    def test_abstract_factory_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            DeviceFactory()
