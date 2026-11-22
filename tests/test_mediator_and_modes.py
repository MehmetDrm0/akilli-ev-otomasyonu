"""MEDIATOR + STATE: sensör olayları HomeHub'a gider, tepkiyi evin modu belirler."""
from akilli_ev import (AtHomeMode, AwayMode, CommandInvoker, HomeHub, Mediator,
                       ModeManager, MotionSensor, NightMode, TemperatureSensor)
from tests.helpers import FakeLight, FakeThermostat, QuietTestCase


class HubTestCase(QuietTestCase):
    def setUp(self):
        super().setUp()
        self.hub = HomeHub(CommandInvoker())
        self.salon, self.mutfak = FakeLight("salon"), FakeLight("mutfak")
        self.thermo = FakeThermostat(target=20)
        self.hub.register_light("salon", self.salon)
        self.hub.register_light("mutfak", self.mutfak)
        self.hub.register_thermostat(self.thermo)
        self.motion = MotionSensor("salon", self.hub)
        self.temp = TemperatureSensor("salon", self.hub)


class MediatorTests(HubTestCase):
    def test_hub_is_a_mediator_and_sensors_only_know_the_mediator(self):
        self.assertIsInstance(self.hub, Mediator)
        self.assertIs(self.motion._mediator, self.hub)

    def test_unknown_event_is_rejected(self):
        with self.assertRaises(ValueError):
            self.hub.notify(self.motion, "duman", None)


class AtHomeModeTests(HubTestCase):
    def test_default_mode_is_at_home(self):
        self.assertEqual(self.hub.modes.current_name, AtHomeMode.name)

    def test_motion_turns_room_light_to_70(self):
        self.motion.trigger()
        self.assertEqual(self.salon.percent, 70)
        self.assertEqual(self.mutfak.percent, 0)

    def test_repeated_motion_does_not_repeat_the_command(self):
        self.motion.trigger()
        self.motion.trigger()
        self.assertEqual(self.salon.history, [70])

    def test_cold_room_raises_target_to_22(self):
        self.temp.report(18)
        self.assertEqual(self.thermo.target, 22)

    def test_comfortable_room_leaves_target_alone(self):
        self.temp.report(21)
        self.assertEqual(self.thermo.history, [])


class NightModeTests(HubTestCase):
    def setUp(self):
        super().setUp()
        self.hub.modes.set_mode("gece")

    def test_motion_gives_dim_night_light(self):
        self.motion.trigger()
        self.assertEqual(self.salon.percent, 15)

    def test_cold_room_target_is_19(self):
        self.temp.report(17)
        self.assertEqual(self.thermo.target, 19)


class AwayModeTests(HubTestCase):
    def setUp(self):
        super().setUp()
        self.salon.percent = self.mutfak.percent = 40
        self.hub.modes.set_mode("uzakta")

    def test_entering_away_turns_lights_off_and_saves_energy(self):
        self.assertEqual((self.salon.percent, self.mutfak.percent), (0, 0))
        self.assertEqual(self.thermo.target, 17)

    def test_motion_while_away_raises_alarm_and_lights_everything(self):
        self.motion.trigger()
        self.assertIn("ALARM", self.output)
        self.assertEqual((self.salon.percent, self.mutfak.percent), (100, 100))

    def test_temperature_does_not_change_energy_saving_target(self):
        before = len(self.thermo.history)
        self.temp.report(25)
        self.assertEqual(len(self.thermo.history), before)

    def test_leaving_away_mode_changes_behaviour(self):
        self.hub.modes.set_mode("evde")
        self.salon.percent = 0
        self.motion.trigger()
        self.assertNotIn("ALARM", self.output)
        self.assertEqual(self.salon.percent, 70)


class ModeManagerTests(HubTestCase):
    def test_unknown_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            self.hub.modes.set_mode("tatil")

    def test_mode_names(self):
        self.assertEqual({AtHomeMode.name, NightMode.name, AwayMode.name},
                         {"Evde", "Gece", "Uzakta"})
        self.assertIsInstance(self.hub.modes, ModeManager)
