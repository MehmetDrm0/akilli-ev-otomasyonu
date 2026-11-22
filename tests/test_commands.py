"""COMMAND: eylemler geri alınabilir; sahne (makro) ters sırada geri alınır."""
from akilli_ev import (CommandInvoker, MacroCommand, SetBrightnessCommand,
                       SetTemperatureCommand)
from tests.helpers import FakeLight, FakeThermostat, QuietTestCase


class CommandTests(QuietTestCase):
    def test_brightness_command_execute_and_undo(self):
        light = FakeLight()
        cmd = SetBrightnessCommand(light, 70)
        cmd.execute()
        self.assertEqual(light.percent, 70)
        cmd.undo()
        self.assertEqual(light.percent, 0)

    def test_temperature_command_execute_and_undo(self):
        thermo = FakeThermostat(target=20)
        cmd = SetTemperatureCommand(thermo, 24)
        cmd.execute()
        self.assertEqual(thermo.target, 24)
        cmd.undo()
        self.assertEqual(thermo.target, 20)

    def test_macro_runs_all_steps_and_undoes_in_reverse_order(self):
        light = FakeLight()
        macro = MacroCommand("deneme", [SetBrightnessCommand(light, 50),
                                        SetBrightnessCommand(light, 80)])
        macro.execute()
        self.assertEqual(light.percent, 80)
        macro.undo()
        self.assertEqual(light.history, [50, 80, 50, 0])   # ters sırada geri alındı
        self.assertEqual(light.percent, 0)

    def test_macro_describe_mentions_name_and_step_count(self):
        macro = MacroCommand("film", [SetBrightnessCommand(FakeLight(), 20)])
        self.assertEqual(macro.describe(), "Sahne 'film' (1 adım)")

    def test_invoker_undoes_last_command_first(self):
        light, inv = FakeLight(), CommandInvoker()
        inv.run(SetBrightnessCommand(light, 30))
        inv.run(SetBrightnessCommand(light, 90))
        inv.undo()
        self.assertEqual(light.percent, 30)
        inv.undo()
        self.assertEqual(light.percent, 0)

    def test_invoker_undo_with_empty_history_raises(self):
        with self.assertRaises(ValueError):
            CommandInvoker().undo()
