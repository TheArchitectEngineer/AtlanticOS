import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('device_intake', ROOT/'tools/device-intake/collect.py')
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)
fb_spec = importlib.util.spec_from_file_location('fastboot_intake', ROOT/'tools/device-intake/fastboot_readonly.py')
fb = importlib.util.module_from_spec(fb_spec)
fb_spec.loader.exec_module(fb)


class IntakeTests(unittest.TestCase):
    def test_single_authorized_transport(self):
        devices = intake.parse_devices('List of devices attached\nfixture device\n\n')
        self.assertEqual(intake.select_device(devices),'fixture')

    def test_unauthorized_and_multiple_require_explicit_selection(self):
        for rows in [[],[('fixture','unauthorized')],[('a','device'),('b','device')],
                     [('a','device'),('b','offline')]]:
            with self.assertRaises(ValueError):
                intake.select_device(rows)
        self.assertEqual(intake.select_device([('a','device'),('b','device')],'b'),'b')

    def test_unknown_commands_are_not_accepted(self):
        for command in ['reboot','flash','root','set_active','shell','battery']:
            with self.assertRaises(ValueError):
                intake.command_for('adb','fixture',command)

    def test_all_queries_use_selected_transport_and_read_only_allowlist(self):
        for name in intake.SHELL_COMMANDS:
            cmd = intake.command_for('adb','fixture',name)
            self.assertEqual(cmd[:4],['adb','-s','fixture','shell'])
            self.assertIn(cmd[4],('getprop','cat','ls','id'))
            self.assertFalse(any(x in cmd for x in ['su','dd','reboot','setprop','flash','set_active']))

    def test_no_battery_or_private_identifier_property(self):
        for prop in intake.PROPERTIES:
            self.assertNotIn('serial',prop)
            self.assertNotIn('imei',prop)
            self.assertNotIn('battery',prop)

    def test_transport_serial_redacted(self):
        self.assertNotIn('fixture-serial',intake.redact('failure fixture-serial','fixture-serial'))

    def test_fastboot_only_explicit_metadata(self):
        for name in fb.VARIABLES:
            self.assertEqual(fb.command_for('fastboot','fixture',name),['fastboot','-s','fixture','getvar',name])
            self.assertNotIn('battery',name)
        for name in ['all','serialno','imei','boot','flash','erase','set_active']:
            with self.assertRaises(ValueError):
                fb.command_for('fastboot','fixture',name)

    def test_fastboot_transport_and_values(self):
        self.assertEqual(fb.select_serial('fixture\tfastboot\n'),'fixture')
        for raw in ['', 'a fastboot\nb fastboot\n', 'a unauthorized\n']:
            with self.assertRaises(ValueError):
                fb.select_serial(raw)
        for raw in ['(bootloader) current-slot: a\nFinished. Total time: 0.001s', 'current-slot: a']:
            self.assertEqual(fb.extract_value('current-slot',raw),'a')
        self.assertIsNone(fb.extract_value('current-slot','FAILED unknown variable'))
