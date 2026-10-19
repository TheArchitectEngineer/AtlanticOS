import hashlib
import json
import struct
import unittest
import zlib

from atlantic_core.policy import BIOS, MockBSP, Target, State
from atlantic_core.validation import (MemoryBlock, validate_primary_gpt, config_encode,
                                     config_load, DEFAULT_CONFIG, image_gate, memory_report)
from atlantic_core.framebuffer import render_png, PATTERNS


def safe_bios(**kwargs):
    return BIOS(MockBSP(targets={'android': Target('android', 'mock', True, True)},
                        android_fallback=True, power_supported=True, **kwargs))


def pulse(bios, key, at, duration=80_000):
    bios.sample(at, {key})
    bios.sample(at+30_000, {key})
    bios.sample(at+duration, set())
    bios.sample(at+duration+30_000, set())


class PolicyTests(unittest.TestCase):
    def test_default_no_unproven_android_message(self):
        b = BIOS()
        b.sample(20_000_000)
        self.assertEqual(b.state, State.RECOVERY)
        self.assertNotIn('Booting Android', '\n'.join(b.lines()))
        self.assertEqual(b.bsp.effects, [])

    def test_exact_countdown_boundary(self):
        b = safe_bios()
        for second in range(5):
            b.sample(second*1_000_000)
            self.assertIn(f'Booting Android in {5-second} seconds...', b.lines())
        b.sample(4_999_999)
        self.assertEqual(b.state, State.COUNTDOWN)
        b.sample(5_000_000)
        self.assertEqual(b.state, State.HANDED_OFF)
        self.assertEqual(b.bsp.effects[-1], 'mock:transfer:android')

    def test_down_held_at_start_no_repeat_when_stuck(self):
        b = safe_bios()
        b.sample(0, {'down'})
        b.sample(30_000, {'down'})
        b.sample(10_000_000, {'down'})
        self.assertEqual((b.state, b.reason, b.selection), (State.MENU, 'KEY_HELD', 0))
        self.assertEqual(b.bsp.effects, [])

    def test_debounce_bounce_then_press(self):
        b = safe_bios()
        for t, k in [(0, set()), (100, {'down'}), (500, set()), (800, {'down'}), (29_000, {'down'})]:
            b.sample(t, k)
        self.assertNotEqual(b.state, State.MENU)
        b.sample(30_800, {'down'})
        self.assertEqual((b.state, b.reason), (State.MENU, 'KEY_PRESSED'))

    def test_down_just_before_deadline_cancels_autoboot(self):
        b = safe_bios()
        b.sample(0)
        b.sample(4_999_999, {'down'})
        b.sample(5_000_000, {'down'})
        self.assertEqual(b.bsp.effects, [])
        b.sample(5_030_000, {'down'})
        self.assertEqual(b.state, State.MENU)

    def test_noise_fails_to_maintenance(self):
        b = safe_bios()
        b.sample(4_999_999, {'down'})
        b.sample(5_000_000)
        b.sample(6_000_000)
        self.assertEqual(b.state, State.RECOVERY)

    def test_double_press_only_one_navigation_after_entry(self):
        b = safe_bios()
        pulse(b, 'down', 0)
        pulse(b, 'down', 200_000)
        self.assertEqual((b.state, b.selection), (State.MENU, 1))

    def test_navigation_wrap_and_missing_media(self):
        b = BIOS()
        b.open_menu('CONFIG')
        b.navigate(-1)
        self.assertEqual(b.selection, len(b.entries())-1)
        for ident in ['usb', 'sd', 'internal', 'file', 'uefi']:
            b.selection = next(i for i,e in enumerate(b.entries()) if e[0] == ident)
            b.activate()
            self.assertIn('UNAVAILABLE', b.message)
        self.assertEqual(b.bsp.effects, [])

    def test_available_but_unverified_stays_blocked(self):
        b = safe_bios()
        b.bsp.targets['android'] = Target('android', 'mock', True, False)
        b.sample(5_000_000)
        self.assertEqual(b.state, State.RECOVERY)

    def test_fallback_boolean_alone_is_not_enough(self):
        b = BIOS(MockBSP(android_fallback=True))
        self.assertEqual(b.state, State.RECOVERY)

    def test_short_power_selects_on_release(self):
        b = safe_bios()
        b.open_menu('CONFIG')
        b.selection = 6
        b.sample(0, {'power'})
        b.sample(30_000, {'power'})
        self.assertEqual(b.state, State.MENU)
        b.sample(80_000)
        b.sample(110_000)
        self.assertEqual(b.state, State.SETUP)

    def test_long_power_confirmation_defaults_to_cancel(self):
        b = safe_bios()
        b.open_menu('CONFIG')
        pulse(b, 'power', 0, 1_600_000)
        self.assertEqual(b.state, State.CONFIRM)
        self.assertFalse(b.confirm_yes)
        pulse(b, 'power', 2_000_000)
        self.assertEqual(b.state, State.MENU)
        self.assertNotIn('mock:power:off', b.bsp.effects)

    def test_stuck_power_only_opens_dialog(self):
        b = safe_bios()
        b.sample(0, {'power'})
        b.sample(30_000, {'power'})
        b.sample(10_000_000, {'power'})
        b.sample(20_000_000, {'power'})
        self.assertEqual(b.state, State.CONFIRM)
        self.assertEqual(b.bsp.effects, [])

    def test_power_off_and_restart_require_separate_confirmation(self):
        for action, state in [('off', State.POWERED_OFF), ('restart', State.RESTARTED)]:
            b = safe_bios()
            b.request_confirmation(action)
            b.navigate(1)
            b.activate()
            self.assertEqual(b.state, state)
            self.assertEqual(b.bsp.effects[-1], f'mock:power:{action}')

    def test_remote_cannot_confirm_power(self):
        b = safe_bios()
        b.request_confirmation('off')
        b.navigate(1)
        b.activate(origin='remote')
        self.assertEqual(b.state, State.RECOVERY)
        self.assertEqual(b.bsp.effects, [])

    def test_unsupported_power(self):
        b = BIOS()
        b.request_confirmation('off')
        self.assertIn('UNSUPPORTED', b.message)
        self.assertEqual(b.bsp.effects, [])

    def test_power_quiesce_failure(self):
        b = safe_bios(quiesce_fail=True)
        b.request_confirmation('restart')
        b.navigate(1)
        b.activate()
        self.assertEqual(b.state, State.RECOVERY)
        self.assertNotIn('mock:power:restart', b.bsp.effects)

    def test_no_framebuffer_has_complete_console_view(self):
        b = safe_bios(framebuffer=False)
        self.assertIn('Press Volume Down to enter AtlanticOS.', b.lines())
        pulse(b, 'down', 0)
        self.assertTrue(any('Boot Menu' in s for s in b.lines()))

    def test_network_default_and_negative_permissions(self):
        b = safe_bios(network=True)
        for consent, auth, protected in [(False, True, True), (True, False, True), (True, True, False)]:
            self.assertEqual(b.request_vnc(consent, auth, protected), 'DENIED')
        self.assertEqual(b.request_vnc(True, True, True), 'UNIMPLEMENTED')
        self.assertFalse(b.network_enabled or b.vnc_enabled)

    def test_partial_handoff_no_retry(self):
        for stage in ['prepare', 'commit']:
            b = safe_bios(handoff_fail_at=stage)
            b.sample(5_000_000)
            b.sample(10_000_000)
            self.assertEqual(b.state, State.RECOVERY)
            self.assertNotIn('mock:transfer:android', b.bsp.effects)
            self.assertEqual(b.bsp.effects.count('mock:prepare:android'), 1)

    def test_handoff_quiesce_failure(self):
        b = safe_bios(quiesce_fail=True)
        b.sample(5_000_000)
        self.assertEqual(b.state, State.RECOVERY)

    def test_clock_reversal_fails_closed(self):
        b = safe_bios()
        b.sample(1_000_000)
        b.sample(999_999)
        self.assertEqual(b.state, State.RECOVERY)

    def test_watchdog_fault(self):
        b = safe_bios()
        b.watchdog_fault()
        b.sample(8_000_000)
        self.assertEqual(b.state, State.RECOVERY)
        self.assertEqual(b.bsp.effects, [])

    def test_settings_navigable_and_locked(self):
        b = safe_bios()
        b.open_menu('CONFIG')
        b.selection = 6
        b.activate()
        b.activate()
        self.assertFalse(b.verbose)
        b.navigate(1)
        b.activate()
        self.assertIn('Locked', b.message)
        b.selection = 5
        b.activate()
        self.assertEqual(b.state, State.MENU)

    def test_invalid_key_rejected(self):
        with self.assertRaises(ValueError):
            BIOS().sample(0, {'magic'})

    def test_committed_handoff_has_no_returning_ui(self):
        b = safe_bios()
        b.sample(5_000_000)
        effects = b.bsp.effects.copy()
        pulse(b, 'power', 6_000_000, 2_000_000)
        self.assertEqual(b.state, State.HANDED_OFF)
        self.assertEqual(b.bsp.effects, effects)


def gpt_fixture():
    data = bytearray(100*512)
    entry = bytearray(128)
    entry[:16], entry[16:32] = b'T'*16, b'U'*16
    struct.pack_into('<QQ', entry, 32, 10, 20)
    table = entry + bytes(128*3)
    data[2*512:3*512] = table
    header = bytearray(512)
    struct.pack_into('<8sIIIIQQQQ16sQIII', header, 0, b'EFI PART', 0x10000, 92, 0, 0,
                     1, 99, 3, 98, b'G'*16, 2, 4, 128, zlib.crc32(table))
    struct.pack_into('<I', header, 16, zlib.crc32(header[:92]))
    data[512:1024] = header
    return bytes(data)


class ValidationTests(unittest.TestCase):
    def test_config_roundtrip(self):
        self.assertEqual(config_load(config_encode())[1], 'OK')

    def test_config_every_truncation(self):
        raw = config_encode()
        for i in range(len(raw)):
            self.assertEqual(config_load(raw[:i]), (DEFAULT_CONFIG, 'SAFE_DEFAULTS'))

    def test_config_unsafe_network_rejected(self):
        for value in [{'vnc':True}, {'network':True}, {'timeout_s':0}, {'version':True}, {'default':'usb'}]:
            self.assertEqual(config_load(config_encode(value))[1], 'SAFE_DEFAULTS')

    def test_config_duplicate_and_oversized(self):
        for raw in [b'{}', b'{"payload":{},"payload":{}}', b'x'*5000, b'[]', b'null', b'"text"', b'\xff']:
            self.assertEqual(config_load(raw)[1], 'SAFE_DEFAULTS')

    def test_config_corrupt_checksum(self):
        raw = config_encode().replace(b'android', b'androix')
        self.assertEqual(config_load(raw)[1], 'SAFE_DEFAULTS')

    def test_block_bounds_and_io_error(self):
        dev = MemoryBlock(bytes(1024), fail_lbas=(1,))
        self.assertEqual(len(dev.read(0)), 512)
        for lba, n in [(-1,1),(2,1),(0,0),(0,3),(2**64,1),(True,1)]:
            with self.assertRaises(ValueError):
                dev.read(lba, n)
        with self.assertRaises(OSError):
            dev.read(1)

    def test_block_not_a_file_or_device_interface(self):
        with self.assertRaises(ValueError):
            MemoryBlock('PhysicalDrive0')
        self.assertFalse(hasattr(MemoryBlock(bytes(512)), 'write'))

    def test_gpt_primary_fixture(self):
        self.assertEqual(validate_primary_gpt(MemoryBlock(gpt_fixture())), [(10,20)])

    def test_gpt_header_mutations(self):
        original = gpt_fixture()
        for offset in range(92):
            data = bytearray(original)
            data[512+offset] ^= 1
            with self.assertRaises(ValueError):
                validate_primary_gpt(MemoryBlock(bytes(data)))

    def test_gpt_table_crc_failure(self):
        data = bytearray(gpt_fixture())
        data[1024] ^= 1
        with self.assertRaises(ValueError):
            validate_primary_gpt(MemoryBlock(bytes(data)))

    def test_gpt_table_bounds_even_with_valid_header_crc(self):
        data = bytearray(gpt_fixture())
        struct.pack_into('<Q', data, 512+72, 99)
        struct.pack_into('<I', data, 512+16, 0)
        struct.pack_into('<I', data, 512+16, zlib.crc32(data[512:512+92]))
        with self.assertRaises(ValueError):
            validate_primary_gpt(MemoryBlock(bytes(data)))

    def test_signature_absent_invalid_and_hash_mismatch(self):
        payload = b'fixture only'
        digest = hashlib.sha256(payload).hexdigest()
        self.assertFalse(image_gate(payload, digest, b'fake'))
        self.assertFalse(image_gate(payload, digest, b'invalid', lambda p,s: False))
        self.assertFalse(image_gate(payload, '0'*64, b'anything', lambda p,s: True))

    def test_memory_includes_framebuffer_and_budget_boundary(self):
        report = memory_report([{'start':0x1000, 'size':100*1024*1024, 'category':'all'}])
        self.assertFalse(report['below_target'])
        report = memory_report([{'start':0, 'size':4_608_000, 'category':'framebuffer'},
                                {'start':0x1000000, 'size':1024, 'category':'tables'}])
        self.assertEqual(report['owned_bytes'], 4_609_024)
        self.assertEqual(report['categories']['framebuffer'], 4_608_000)

    def test_memory_overlap_and_overflow_rejected(self):
        for regions in [ [{'start':0,'size':100,'category':'x'}, {'start':50,'size':100,'category':'y'}],
                         [{'start':2**64-1,'size':2,'category':'x'}] ]:
            with self.assertRaises(ValueError):
                memory_report(regions)

    def test_render_all_screens_no_clipping(self):
        b = safe_bios()
        for state in State:
            b.state = state
            result = render_png(b.lines())
            self.assertEqual(result[:8], b'\x89PNG\r\n\x1a\n')
        self.assertTrue(all(len(p.split('/')) == 7 for p in PATTERNS.values()))


if __name__ == '__main__':
    unittest.main()
