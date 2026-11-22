"""ADAPTER: üretici SDK'larının birim/ölçek dönüşümleri yalnızca adaptörlerde yapılır."""
from akilli_ev import (Light, LumaBridge, LumaLightAdapter, LumaThermostatAdapter,
                       NovaLightAdapter, NovaThermostatAdapter, Thermostat)
from tests.helpers import QuietTestCase, RecordingBridge, RecordingCloud


class AdapterTests(QuietTestCase):
    def test_luma_light_converts_percent_to_0_254(self):
        bridge = RecordingBridge()
        light = LumaLightAdapter("salon", bridge)
        light.set_brightness(50)
        self.assertEqual(bridge.sent, [("luma-light-salon", {"on": True, "bri": 127})])
        self.assertEqual(light.get_brightness(), 50)

    def test_luma_light_zero_means_off(self):
        bridge = RecordingBridge()
        LumaLightAdapter("salon", bridge).set_brightness(0)
        self.assertEqual(bridge.sent[0][1], {"on": False, "bri": 0})

    def test_luma_thermostat_converts_celsius_to_fahrenheit(self):
        bridge = RecordingBridge()
        thermo = LumaThermostatAdapter("ana", bridge)
        thermo.set_target(22)
        self.assertEqual(bridge.sent, [("luma-thermo-ana", {"target_f": 71.6})])
        self.assertEqual(thermo.get_target(), 22)

    def test_nova_light_converts_percent_to_level_0_10(self):
        cloud = RecordingCloud()
        light = NovaLightAdapter("mutfak", cloud)
        light.set_brightness(50)
        self.assertEqual(cloud.calls, [("light_set", "nova-light-mutfak", 5)])

    def test_nova_thermostat_converts_to_deci_celsius(self):
        cloud = RecordingCloud()
        NovaThermostatAdapter("ana", cloud).set_target(22.5)
        self.assertEqual(cloud.calls, [("climate_set", "nova-climate-ana", 225)])

    def test_adapters_satisfy_target_interfaces(self):
        light = LumaLightAdapter("a", RecordingBridge())
        thermo = NovaThermostatAdapter("b", RecordingCloud())
        self.assertIsInstance(light, Light)
        self.assertIsInstance(thermo, Thermostat)

    def test_state_is_not_updated_when_send_fails(self):
        light = LumaLightAdapter("salon", LumaBridge(fail_times=1))
        with self.assertRaises(ConnectionError):
            light.set_brightness(80)
        self.assertEqual(light.get_brightness(), 0)

    def test_target_interfaces_are_abstract(self):
        with self.assertRaises(TypeError):
            Light("x")
        with self.assertRaises(TypeError):
            Thermostat("x")
