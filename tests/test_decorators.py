"""DECORATOR: davranışlar bağımsız, birleştirilebilir ve çalışma anında eklenir."""
from akilli_ev import (BrightnessLimitedLight, Light, LightDecorator, LoggedLight,
                       LumaBridge, LumaLightAdapter, RetryLight)
from tests.helpers import FakeLight, FakeThermostat, QuietTestCase


class DecoratorTests(QuietTestCase):
    def test_limit_clamps_values_above_maximum(self):
        base = FakeLight()
        BrightnessLimitedLight(base, 60).set_brightness(100)
        self.assertEqual(base.history, [60])

    def test_limit_passes_values_below_maximum(self):
        base = FakeLight()
        BrightnessLimitedLight(base, 60).set_brightness(40)
        self.assertEqual(base.history, [40])

    def test_retry_succeeds_after_transient_failures(self):
        base = FakeLight(fail_times=2)
        RetryLight(base, tries=3).set_brightness(50)
        self.assertEqual(base.history, [50])
        self.assertEqual(self.output.count("başarısız"), 2)

    def test_retry_raises_when_attempts_are_exhausted(self):
        base = FakeLight(fail_times=3)
        with self.assertRaises(ConnectionError):
            RetryLight(base, tries=3).set_brightness(50)

    def test_log_writes_requested_value(self):
        LoggedLight(FakeLight("salon")).set_brightness(70)
        self.assertIn("salon: %70 isteniyor", self.output)

    def test_decorators_stack_and_describe_the_chain(self):
        chain = LoggedLight(BrightnessLimitedLight(RetryLight(FakeLight("a"), 3), 60))
        self.assertEqual(chain.describe(), "Sahte ışık (a), Retry×3, Max%60, Log")

    def test_full_chain_applies_every_behaviour(self):
        base = FakeLight("a", fail_times=2)
        chain = LoggedLight(BrightnessLimitedLight(RetryLight(base, 3), 60))
        chain.set_brightness(100)
        self.assertEqual(base.history, [60])
        self.assertIn("%100 isteniyor", self.output)

    def test_order_matters_for_what_gets_logged(self):
        LoggedLight(BrightnessLimitedLight(FakeLight(), 60)).set_brightness(100)
        self.assertIn("%100 isteniyor", self.output)
        self.clear_output()
        BrightnessLimitedLight(LoggedLight(FakeLight()), 60).set_brightness(100)
        self.assertIn("%60 isteniyor", self.output)

    def test_get_brightness_and_name_are_delegated(self):
        base = FakeLight("salon")
        deco = LoggedLight(base)
        deco.set_brightness(30)
        self.assertEqual(deco.get_brightness(), 30)
        self.assertEqual(deco.name, "salon")

    def test_decorated_light_is_still_a_light(self):
        deco = LoggedLight(LumaLightAdapter("a", LumaBridge()))
        self.assertIsInstance(deco, Light)
        self.assertNotIsInstance(deco, LumaLightAdapter)   # somut tip kimliği kaybolur

    def test_non_light_cannot_be_wrapped(self):
        with self.assertRaises(TypeError):
            BrightnessLimitedLight(FakeThermostat())

    def test_decorator_base_is_abstract(self):
        with self.assertRaises(TypeError):
            LightDecorator(FakeLight())

    def test_new_decorator_needs_no_change_to_existing_classes(self):
        class MinBrightnessLight(LightDecorator):          # yalnızca yeni bir sınıf
            def set_brightness(self, percent):
                self._inner.set_brightness(max(percent, 10) if percent > 0 else 0)

            def describe(self):
                return self._inner.describe() + ", Min%10"

        base = FakeLight()
        light = LoggedLight(MinBrightnessLight(base))
        light.set_brightness(3)
        self.assertEqual(base.history, [10])
        self.assertTrue(light.describe().endswith("Min%10, Log"))
