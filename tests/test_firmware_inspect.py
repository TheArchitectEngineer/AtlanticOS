import importlib.util
import io
from pathlib import Path
import struct
import unittest
import gzip

spec = importlib.util.spec_from_file_location('firmware_inspect', Path(__file__).resolve().parents[1] / 'tools/firmware_inspect.py')
fw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fw)


def pac_fixture():
    end = fw.PAC_HEADER + fw.PAC_RECORD
    data = bytearray(end + 16)
    version = 'BP_R2.0.1'.encode('utf-16-le')
    data[:len(version)] = version
    for at, value in [(0x30, len(data)), (0x434, 1), (0x438, fw.PAC_HEADER),
                      (0x844, 0xfffafffa), (fw.PAC_HEADER, fw.PAC_RECORD),
                      (fw.PAC_HEADER + 0x604, 16), (fw.PAC_HEADER + 0x610, end)]:
        struct.pack_into('<I', data, at, value)
    data[fw.PAC_HEADER + 4:fw.PAC_HEADER + 12] = 'BOOT'.encode('utf-16-le')
    name = 'boot.img'.encode('utf-16-le')
    data[fw.PAC_HEADER + 0x204:fw.PAC_HEADER + 0x204 + len(name)] = name
    return data


def boot_fixture():
    data = bytearray(8192)
    data[:8] = b'ANDROID!'
    for at, value in [(8, 16), (16, 16), (36, 2048), (40, 2), (1644, 1660), (1648, 40)]:
        struct.pack_into('<I', data, at, value)
    return data


def dt_fixture():
    data = bytearray(104)
    struct.pack_into('>8I', data, 0, 0xd7b7ab1e, 104, 32, 32, 1, 32, 2048, 0)
    struct.pack_into('>8I', data, 32, 40, 64, 0, 0, 0, 0, 0, 0)
    struct.pack_into('>2I', data, 64, 0xd00dfeed, 40)
    return data


def cpio_record(name, content, mode=0x81a4):
    encoded = name.encode() + b'\0'
    fields = [0, mode, 0, 0, 1, 0, len(content), 0, 0, 0, 0, len(encoded), 0]
    b = b'070701' + ''.join(f'{v:08x}' for v in fields).encode() + encoded
    b += bytes((-len(b)) % 4)
    b += content
    return b + bytes((-len(b)) % 4)


class FirmwareInspectTests(unittest.TestCase):
    def test_pac_valid(self):
        b = pac_fixture()
        r = fw.inspect_pac(io.BytesIO(b), len(b))
        self.assertEqual(r['entries'][0]['name'], 'boot.img')
        self.assertEqual(r['oem_authentication'], 'NOT_VERIFIED')

    def test_pac_truncation_and_large_high_words(self):
        original = pac_fixture()
        for cut in [0, 40, fw.PAC_HEADER - 1, len(original) - 1]:
            with self.assertRaises(ValueError):
                fw.inspect_pac(io.BytesIO(original[:cut]), cut)
        for field in [0x5fc, 0x600]:
            b = pac_fixture()
            struct.pack_into('<I', b, fw.PAC_HEADER + field, 1)
            with self.assertRaises(ValueError):
                fw.inspect_pac(io.BytesIO(b), len(b))

    def test_pac_overlaps_and_unsupported_headers(self):
        for at, value in [(0x434, 0), (0x434, 257), (0x438, 0), (0x844, 0),
                          (fw.PAC_HEADER, 8), (fw.PAC_HEADER + 0x610, 0)]:
            b = pac_fixture()
            struct.pack_into('<I', b, at, value)
            with self.assertRaises(ValueError):
                fw.inspect_pac(io.BytesIO(b), len(b))

    def test_pac_path_injection(self):
        for name in ['../x', '..\\x', 'C:x']:
            b = pac_fixture()
            b[fw.PAC_HEADER + 0x204:fw.PAC_HEADER + 0x5fc] = bytes(0x3f8)
            encoded = name.encode('utf-16-le')
            b[fw.PAC_HEADER + 0x204:fw.PAC_HEADER + 0x204 + len(encoded)] = encoded
            with self.assertRaises(ValueError):
                fw.inspect_pac(io.BytesIO(b), len(b))

    def test_pac_overlapping_payloads(self):
        b = pac_fixture()
        second = bytearray(b[fw.PAC_HEADER:fw.PAC_HEADER + fw.PAC_RECORD])
        second[4:12] = 'TEST'.encode('utf-16-le')
        second[0x204:0x214] = 'test.img'.encode('utf-16-le')
        b = b[:fw.PAC_HEADER + fw.PAC_RECORD] + second + bytes(32)
        start = fw.PAC_HEADER + 2 * fw.PAC_RECORD
        struct.pack_into('<I', b, 0x30, len(b))
        struct.pack_into('<I', b, 0x434, 2)
        for at in [fw.PAC_HEADER, fw.PAC_HEADER + fw.PAC_RECORD]:
            struct.pack_into('<I', b, at + 0x610, start)
        with self.assertRaisesRegex(ValueError, 'Overlapping'):
            fw.inspect_pac(io.BytesIO(b), len(b))

    def test_pac_high_words_preserve_64_bit_offsets(self):
        b = pac_fixture()
        total = (1 << 32) + len(b)
        struct.pack_into('<I', b, 0x2c, 1)
        struct.pack_into('<I', b, fw.PAC_HEADER + 0x600, 1)
        # Directory parsing reads metadata only; synthetic file has no payload.
        r = fw.inspect_pac(io.BytesIO(b), total)
        self.assertEqual(r['entries'][0]['offset'], (1 << 32) + fw.PAC_HEADER + fw.PAC_RECORD)

    def test_boot_standard_sections(self):
        r = fw.inspect_boot(boot_fixture())
        self.assertEqual(r['header_version'], 2)
        self.assertEqual([s['offset'] for s in r['sections']], [2048, 4096, 6144, 6144, 6144])
        self.assertEqual(r['standard_sections_end'], 8192)

    def test_boot_bounds_version_and_inconsistent_recovery(self):
        for at, value in [(8, 0xffffffff), (16, 0), (36, 2000), (36, 1 << 20),
                          (40, 4), (1644, 0), (1632, 32), (1648, 0xffffffff)]:
            b = boot_fixture()
            struct.pack_into('<I', b, at, value)
            with self.assertRaises(ValueError):
                fw.inspect_boot(b)
        for size in [0, 47, 2047, 8191]:
            with self.assertRaises(ValueError):
                fw.inspect_boot(boot_fixture()[:size])

    def test_dt_table_bounded_entries(self):
        r = fw.inspect_dt_table(dt_fixture())
        self.assertEqual(r['entries'][0]['offset'], 64)
        for at, value in [(0, 0), (4, 105), (12, 16), (16, 257), (20, 0),
                          (28, 1), (32, 41), (36, 0), (68, 41)]:
            b = dt_fixture()
            struct.pack_into('>I', b, at, value)
            with self.assertRaises(ValueError):
                fw.inspect_dt_table(b)

    def test_ramdisk_identity_and_inert_symlinks(self):
        b = cpio_record('default.prop', b'prop.default', 0xa1ff)
        b += cpio_record('prop.default', b'ro.build.id=FIXTURE\nsecret=not-published\n')
        b += cpio_record('TRAILER!!!', b'')
        r = fw.inspect_ramdisk(gzip.compress(b))
        self.assertEqual(r['properties'][0]['values'], {'ro.build.id': 'FIXTURE'})
        self.assertFalse(r['archive_entries_executed_or_installed'])

    def test_ramdisk_limits_truncation_and_missing_trailer(self):
        b = cpio_record('prop.default', b'ro.build.id=FIXTURE\n')
        valid = gzip.compress(b + cpio_record('TRAILER!!!', b''))
        for data, limit in [(valid, 8), (valid[:-1], 4096),
                            (valid + valid, 4096), (gzip.compress(b), 4096)]:
            with self.assertRaises(ValueError):
                fw.inspect_ramdisk(data, limit)

    def test_ramdisk_duplicate_identity_and_bad_names(self):
        b = cpio_record('prop.default', b'ro.build.id=A\nro.build.id=B\n')
        with self.assertRaises(ValueError):
            fw.inspect_ramdisk(gzip.compress(b + cpio_record('TRAILER!!!', b'')))
        b = bytearray(cpio_record('prop.default', b''))
        b[110 + len('prop.default')] = 65
        with self.assertRaises(ValueError):
            fw.inspect_ramdisk(gzip.compress(b + cpio_record('TRAILER!!!', b'')))


if __name__ == '__main__':
    unittest.main()
