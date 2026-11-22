"""FACADE: istemci yalnızca SmartHomeFacade ile konuşur (uçtan uca senaryolar)."""
from akilli_ev import (BrightnessLimitedLight, LoggedLight, LumaFactory, NovaFactory,
                       SmartHomeFacade)
from tests.helpers import QuietTestCase


def make_home():
    home = SmartHomeFacade()
    home.add_light("salon", LumaFactory())
    home.add_light("mutfak", NovaFactory())
    home.add_light("yatak odası", NovaFactory())
    home.set_thermostat(LumaFactory())
    return home


class FacadeTests(QuietTestCase):
    def test_movie_scene_sets_lights_and_temperature(self):
        home = make_home()
        home.run_scene("film")
        self.assertEqual(home.brightness("salon"), 20)
        self.assertEqual(home.brightness("mutfak"), 0)
        self.assertEqual(home.target_temperature(), 22)

    def test_sleep_scene_turns_everything_off(self):
        home = make_home()
        home.set_light("salon", 80)
        home.run_scene("uyku")
        self.assertEqual([home.brightness(r) for r in ("salon", "mutfak", "yatak odası")], [0, 0, 0])
        self.assertEqual(home.target_temperature(), 19)

    def test_undo_restores_previous_state(self):
        home = make_home()
        home.set_light("salon", 50)
        home.run_scene("film")
        home.undo()
        self.assertEqual(home.brightness("salon"), 50)
        self.assertEqual(home.target_temperature(), 20)

    def test_same_scene_twice_then_undo_twice_is_consistent(self):
        home = make_home()
        home.run_scene("film")
        home.run_scene("film")
        home.undo()
        self.assertEqual(home.brightness("salon"), 20)
        home.undo()
        self.assertEqual(home.brightness("salon"), 0)
        self.assertEqual(home.target_temperature(), 20)

    def test_unknown_scene_is_rejected(self):
        with self.assertRaises(ValueError):
            make_home().run_scene("parti")

    def test_undo_without_history_is_rejected(self):
        with self.assertRaises(ValueError):
            make_home().undo()

    def test_mode_switch_and_motion_through_facade(self):
        home = make_home()
        home.set_mode("gece")
        self.assertEqual(home.mode_name(), "Gece")
        home.motion("mutfak")
        self.assertEqual(home.brightness("mutfak"), 15)

    def test_away_mode_alarm_end_to_end(self):
        home = make_home()
        home.set_mode("uzakta")
        home.motion("salon")
        self.assertIn("ALARM", self.output)
        self.assertEqual(home.brightness("yatak odası"), 100)

    def test_wrap_light_adds_decorators_at_runtime(self):
        home = make_home()
        home.wrap_light("salon", BrightnessLimitedLight, max_percent=60)
        home.wrap_light("salon", LoggedLight)
        self.assertEqual(home.describe_light("salon"), "Luma ışık (salon), Max%60, Log")
        home.set_light("salon", 100)
        self.assertEqual(home.brightness("salon"), 60)

    def test_commands_work_through_decorated_light_and_undo(self):
        home = make_home()
        home.wrap_light("salon", BrightnessLimitedLight, max_percent=60)
        home.set_light("salon", 100)
        home.undo()
        self.assertEqual(home.brightness("salon"), 0)
