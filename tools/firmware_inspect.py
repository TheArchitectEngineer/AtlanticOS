"""Original offline PAC/Android boot inspector; never opens a device transport.

PAC BP_R2.0.1 field offsets were inferred from the downloaded p352 sample.
This deliberately supports one PAC dialect and Android boot v0-v2, not flashing.
CRC, hashes and plausible headers do not authenticate an OEM signing key.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
PAC_HEADER = 0x84c
PAC_RECORD = 0xa14
MAX_RECORDS = 256
EXTRACT = {'boot.img': 128 << 20, 'dtbo.img': 16 << 20,
           'p352.xml': 1 << 20, 'vbmeta-sign.img': 2 << 20,
           'u-boot-sign.bin': 2 << 20}
PROP_KEYS = frozenset(('ro.build.fingerprint', 'ro.build.id',
                       'ro.build.version.incremental', 'ro.build.version.security_patch',
                       'ro.bootimage.build.fingerprint', 'ro.carrier'))


def u32(data, at, endian='<'):
    if at < 0 or at + 4 > len(data):
        raise ValueError('Truncated integer')
    return struct.unpack_from(endian + 'I', data, at)[0]


def text16(data):
    try:
        text = data.decode('utf-16-le').split('\0', 1)[0]
    except UnicodeError as e:
        raise ValueError('Invalid UTF-16 field') from e
    if any(ord(c) < 32 for c in text):
        raise ValueError('Control character in PAC name')
    return text


def bounded(at, length, total):
    if at < 0 or length < 0 or at > total or length > total - at:
        raise ValueError('Range outside file')


def inspect_pac(stream, total):
    if not PAC_HEADER <= total <= 16 << 30:
        raise ValueError('Unsupported PAC size')
    stream.seek(0)
    header = stream.read(PAC_HEADER)
    if len(header) != PAC_HEADER:
        raise ValueError('Truncated PAC header')
    if text16(header[:0x2c]) != 'BP_R2.0.1':
        raise ValueError('Unsupported PAC dialect')
    declared = u32(header, 0x30) | (u32(header, 0x2c) << 32)
    if declared != total or u32(header, 0x844) != 0xfffafffa:
        raise ValueError('PAC length or marker mismatch')
    count, start = u32(header, 0x434), u32(header, 0x438)
    if not 1 <= count <= MAX_RECORDS or start != PAC_HEADER:
        raise ValueError('Unsupported PAC directory')
    table_end = start + count * PAC_RECORD
    bounded(start, count * PAC_RECORD, total)
    table = stream.read(count * PAC_RECORD)
    if len(table) != count * PAC_RECORD:
        raise ValueError('Truncated PAC directory')
    entries, ranges, names, ids = [], [], set(), set()
    for index in range(count):
        r = table[index * PAC_RECORD:(index + 1) * PAC_RECORD]
        if u32(r, 0) != PAC_RECORD:
            raise ValueError('Unsupported PAC record size')
        ident, name = text16(r[4:0x204]), text16(r[0x204:0x5fc])
        if name and (name in names or '/' in name or '\\' in name or ':' in name
                     or name in ('.', '..')):
            raise ValueError('Duplicate or non-leaf PAC filename')
        if ident and ident in ids:
            raise ValueError('Duplicate PAC identifier')
        names.add(name)
        ids.add(ident)
        size = u32(r, 0x604) | (u32(r, 0x5fc) << 32)
        offset = u32(r, 0x610) | (u32(r, 0x600) << 32)
        if size:
            bounded(offset, size, total)
            if offset < table_end or not name:
                raise ValueError('Payload overlaps directory or lacks a name')
            ranges.append((offset, offset + size))
        elif offset or name:
            raise ValueError('Unsupported empty PAC record')
        entries.append({'index': index, 'id': ident, 'name': name,
                        'offset': offset, 'size': size})
    ranges.sort()
    if any(a[1] > b[0] for a, b in zip(ranges, ranges[1:])):
        raise ValueError('Overlapping PAC payloads')
    return {'dialect': 'BP_R2.0.1', 'bytes': total, 'entry_count': count,
            'directory_end': table_end, 'entries': entries,
            'pac_internal_crc': 'NOT_IMPLEMENTED',
            'oem_authentication': 'NOT_VERIFIED'}


def inspect_boot(data):
    """Interpret standard layout only; header load fields are not runtime proof."""
    if len(data) < 48 or data[:8] != b'ANDROID!':
        raise ValueError('Missing Android boot magic')
    version = u32(data, 40)
    sizes = {0: 1632, 1: 1648, 2: 1660}
    if version not in sizes:
        raise ValueError('Only Android boot header v0-v2 supported')
    header_size = sizes[version]
    page = u32(data, 36)
    if page < header_size or page > 65536 or page & (page - 1):
        raise ValueError('Invalid boot page size')
    bounded(0, page, len(data))
    if version and u32(data, 1644) != header_size:
        raise ValueError('Inconsistent boot header size')
    align = lambda n: (n + page - 1) // page * page
    cursor, sections = page, []
    for name, size_at, addr_at in [('kernel', 8, 12), ('ramdisk', 16, 20),
                                    ('second', 24, 28)]:
        size = u32(data, size_at)
        bounded(cursor, align(size), len(data))
        sections.append({'name': name, 'offset': cursor, 'size': size,
                         'header_load_field': u32(data, addr_at)})
        cursor += align(size)
    if not sections[0]['size'] or not sections[1]['size']:
        raise ValueError('Missing kernel or ramdisk')
    if version:
        size = u32(data, 1632)
        offset = struct.unpack_from('<Q', data, 1636)[0]
        if size and offset != cursor:
            raise ValueError('Nonstandard recovery DTBO layout')
        bounded(cursor, align(size), len(data))
        sections.append({'name': 'recovery_dtbo', 'offset': cursor, 'size': size})
        cursor += align(size)
    if version == 2:
        size = u32(data, 1648)
        bounded(cursor, align(size), len(data))
        sections.append({'name': 'dtb', 'offset': cursor, 'size': size,
                         'header_load_field': struct.unpack_from('<Q', data, 1652)[0]})
        cursor += align(size)
    for s in sections:
        content = data[s['offset']:s['offset'] + s['size']]
        s['sha256'] = hashlib.sha256(content).hexdigest()
        s['prefix_hex'] = content[:16].hex()
    os = u32(data, 44)
    return {'header_version': version, 'header_size': header_size, 'page_size': page,
            'os_version': '.'.join(str((os >> shift) & 127) for shift in (25, 18, 11)),
            'patch_month': f'{2000 + ((os >> 4) & 127):04d}-{os & 15:02d}',
            'tags_header_field': u32(data, 32), 'sections': sections,
            'standard_sections_end': cursor, 'trailing_bytes': len(data) - cursor,
            'load_fields_interpretation': 'HEADER_VALUES_ONLY_NOT_RUNTIME_ADDRESSES'}


def inspect_dt_table(data):
    """AOSP dt_table header/entries. FDT internals are a separate validation."""
    if len(data) < 32 or u32(data, 0, '>') != 0xd7b7ab1e:
        raise ValueError('Missing Android DT table magic')
    total, hdr, stride, count, start, page, version = struct.unpack_from('>7I', data, 4)
    if total > len(data) or total < 32 or hdr != 32 or stride != 32 or version != 0:
        raise ValueError('Unsupported DT table header')
    if not 1 <= count <= 256 or start < hdr or page < 512 or page & (page - 1):
        raise ValueError('Invalid DT table parameters')
    bounded(start, count * stride, total)
    end = start + count * stride
    entries, ranges = [], []
    for index in range(count):
        size, offset, ident, revision, *custom = struct.unpack_from('>8I', data, start + index * stride)
        bounded(offset, size, total)
        if offset < end or size < 40:
            raise ValueError('DTB overlaps table or is too small')
        blob = data[offset:offset + size]
        if blob[:4] != b'\xd0\x0d\xfe\xed' or u32(blob, 4, '>') != size:
            raise ValueError('DT entry is not a complete FDT blob')
        ranges.append((offset, offset + size))
        entries.append({'index': index, 'offset': offset, 'size': size,
                        'id': ident, 'revision': revision, 'custom': custom,
                        'sha256': hashlib.sha256(blob).hexdigest()})
    ranges.sort()
    if any(a[1] > b[0] for a, b in zip(ranges, ranges[1:])):
        raise ValueError('Overlapping DT blobs')
    return {'total_size': total, 'page_size': page, 'version': version, 'entries': entries}


def inspect_ramdisk(data, max_bytes=64 << 20):
    """Bounded gzip/newc metadata reader; never creates archive paths or links."""
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        unpacked = decoder.decompress(data, max_bytes + 1)
    except zlib.error as e:
        raise ValueError('Invalid gzip ramdisk') from e
    if len(unpacked) > max_bytes or not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:
        raise ValueError('Ramdisk too large, truncated or has extra gzip members')
    cursor, properties, trailer = 0, [], False
    for _ in range(32768):
        bounded(cursor, 110, len(unpacked))
        header = unpacked[cursor:cursor + 110]
        if header[:6] != b'070701' or any(c not in b'0123456789abcdefABCDEF' for c in header[6:]):
            raise ValueError('Unsupported or malformed newc header')
        fields = [int(header[6 + i * 8:14 + i * 8], 16) for i in range(13)]
        mode, size, name_size = fields[1], fields[6], fields[11]
        if not 1 <= name_size <= 1024:
            raise ValueError('Invalid newc name length')
        bounded(cursor + 110, name_size, len(unpacked))
        raw_name = unpacked[cursor + 110:cursor + 110 + name_size]
        if raw_name[-1] or b'\0' in raw_name[:-1]:
            raise ValueError('Unterminated or ambiguous newc name')
        try:
            name = raw_name[:-1].decode('utf-8')
        except UnicodeError as e:
            raise ValueError('Invalid newc filename encoding') from e
        start = (cursor + 110 + name_size + 3) & ~3
        bounded(start, size, len(unpacked))
        end = (start + size + 3) & ~3
        bounded(0, end, len(unpacked))
        if name == 'TRAILER!!!':
            if size or any(unpacked[end:]):
                raise ValueError('Invalid newc trailer')
            trailer = True
            break
        # Only regular property files are considered; symlinks remain inert.
        if name in ('prop.default', 'default.prop') and mode & 0xf000 == 0x8000:
            if size > 1 << 20 or any(p['file'] == name for p in properties):
                raise ValueError('Oversized or duplicate property file')
            content = unpacked[start:start + size]
            values = {}
            for line in content.decode('utf-8').splitlines():
                key, sep, value = line.partition('=')
                if sep and key in PROP_KEYS:
                    if key in values:
                        raise ValueError('Duplicate identity property')
                    values[key] = value
            properties.append({'file': name, 'sha256': hashlib.sha256(content).hexdigest(),
                               'values': values})
        cursor = end
    if not trailer:
        raise ValueError('Missing newc trailer or record limit exceeded')
    return {'unpacked_bytes': len(unpacked), 'properties': properties,
            'archive_entries_executed_or_installed': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True,
                    help='New private directory beneath this checkout work/')
    args = ap.parse_args()
    # Reject block devices and Windows device namespace paths before opening.
    raw = str(args.input)
    if raw.startswith(('\\\\.\\', '\\\\?\\')) or not args.input.is_file():
        ap.error('Input must be a regular offline file')
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / 'work').resolve()):
        ap.error('Firmware outputs must remain in ignored work/')
    with args.input.open('rb') as source:
        st = os.fstat(source.fileno())
        if not stat.S_ISREG(st.st_mode):
            ap.error('Input must be a regular file')
        report = inspect_pac(source, st.st_size)
        selected = [e for e in report['entries'] if e['name'] in EXTRACT]
        if any(e['size'] > EXTRACT[e['name']] for e in selected):
            ap.error('Selected payload exceeds research limit')
        if not any(e['name'] == 'boot.img' for e in selected):
            ap.error('No boot.img in supported PAC')
        output.mkdir(parents=True, exist_ok=False)
        report.update(label='HOST_TESTED', scope='OFFLINE_DOWNLOADED_FIRMWARE_ONLY',
                      firmware_executed=False, phone_accessed=False,
                      source_path_published=False, extracted=[])
        for e in selected:
            source.seek(e['offset'])
            content = source.read(e['size'])
            if len(content) != e['size']:
                raise ValueError('Input changed or truncated during extraction')
            (output / e['name']).write_bytes(content)
            item = {**e, 'sha256': hashlib.sha256(content).hexdigest()}
            if e['name'] == 'boot.img':
                item['boot'] = inspect_boot(content)
                for s in item['boot']['sections']:
                    if s['size'] and s['name'] == 'ramdisk':
                        item['ramdisk_identity'] = inspect_ramdisk(content[s['offset']:s['offset'] + s['size']])
                    if s['size'] and s['name'] == 'dtb':
                        section = content[s['offset']:s['offset'] + s['size']]
                        (output / 'boot-dtb.bin').write_bytes(section)
                        item['boot_dt_table'] = inspect_dt_table(section)
                        for d in item['boot_dt_table']['entries']:
                            (output / f'boot-dtb-{d["index"]}.dtb').write_bytes(section[d['offset']:d['offset'] + d['size']])
            if e['name'] == 'dtbo.img':
                item['dt_table'] = inspect_dt_table(content)
                for d in item['dt_table']['entries']:
                    (output / f'dtbo-{d["index"]}.dtb').write_bytes(content[d['offset']:d['offset'] + d['size']])
            report['extracted'].append(item)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'label': report['label'], 'entries': report['entry_count'],
                      'output': str(output), 'phone_accessed': False}))


if __name__ == '__main__':
    main()
