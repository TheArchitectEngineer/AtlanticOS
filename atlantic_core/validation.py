"""Host validation helpers operating on byte buffers, never block devices."""
import hashlib
import json
import struct
import zlib


DEFAULT_CONFIG = {"version": 1, "default": "android", "timeout_s": 5,
                  "network": False, "vnc": False, "verbose": True}


def config_encode(values=None):
    payload = {**DEFAULT_CONFIG, **(values or {})}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    # Corruption detection only; this digest is not authentication.
    return json.dumps({"payload": payload, "sha256": hashlib.sha256(raw).hexdigest()},
                      sort_keys=True).encode("ascii")


def _unique_object(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError("duplicate JSON key")
        obj[k] = v
    return obj


def config_load(raw):
    try:
        if len(raw) > 4096:
            raise ValueError("oversized")
        envelope = json.loads(raw, object_pairs_hook=_unique_object)
        if set(envelope) != {"payload", "sha256"}:
            raise ValueError("envelope")
        p = envelope["payload"]
        if set(p) != set(DEFAULT_CONFIG):
            raise ValueError("fields")
        if (type(p["version"]) is not int or p["version"] != 1 or p["default"] != "android"
                or type(p["timeout_s"]) is not int or p["timeout_s"] != 5
                or any(type(p[k]) is not bool for k in ("network", "vnc", "verbose"))
                or p["network"] or p["vnc"]):
            raise ValueError("unsafe or unsupported configuration")
        canonical = json.dumps(p, sort_keys=True, separators=(",", ":")).encode("ascii")
        if envelope["sha256"] != hashlib.sha256(canonical).hexdigest():
            raise ValueError("corrupt")
        return p, "OK"
    except (ValueError, TypeError, KeyError, UnicodeError, AttributeError):
        return DEFAULT_CONFIG.copy(), "SAFE_DEFAULTS"


class MemoryBlock:
    """Only a bytes fixture is accepted. No path / drive / partition operations."""
    def __init__(self, data, sector_size=512, fail_lbas=()):
        if type(data) is not bytes or sector_size not in (512, 4096) or len(data) % sector_size:
            raise ValueError("unaligned fixture")
        self.data, self.sector_size, self.fail_lbas = data, sector_size, set(fail_lbas)

    @property
    def count(self):
        return len(self.data) // self.sector_size

    def read(self, lba, sectors=1):
        if type(lba) is not int or type(sectors) is not int or lba < 0 or sectors <= 0 or lba >= self.count or sectors > self.count - lba:
            raise ValueError("block out of range")
        if any(lba <= f < lba + sectors for f in self.fail_lbas):
            raise OSError("injected read error")
        return self.data[lba*self.sector_size:(lba+sectors)*self.sector_size]


def validate_primary_gpt(dev):
    """Bounded host-only primary GPT validator; not a filesystem or firmware driver.

    Backup GPT and protective MBR are deliberately not validated here: this helper
    can never enable a boot source, even when it returns a partition list.
    """
    header = dev.read(1)
    signature, revision, size, checksum, reserved = struct.unpack_from("<8sIIII", header)
    if signature != b"EFI PART" or revision != 0x10000 or not 92 <= size <= dev.sector_size or reserved:
        raise ValueError("GPT header")
    copy = bytearray(header[:size])
    copy[16:20] = bytes(4)
    if zlib.crc32(copy) != checksum:
        raise ValueError("GPT header CRC")
    current, backup, first, last = struct.unpack_from("<QQQQ", header, 24)
    table_lba, count, entry_size, table_crc = struct.unpack_from("<QIII", header, 72)
    total = count * entry_size
    if current != 1 or backup != dev.count-1 or not 2 <= first <= last < backup:
        raise ValueError("GPT geometry")
    if not 1 <= count <= 4096 or entry_size < 128 or entry_size % 128 or total > 4*1024*1024:
        raise ValueError("GPT table limits")
    sectors = (total + dev.sector_size-1) // dev.sector_size
    if table_lba < 2 or table_lba + sectors > first:
        raise ValueError("GPT table overlap")
    table = dev.read(table_lba, sectors)[:total]
    if zlib.crc32(table) != table_crc:
        raise ValueError("GPT table CRC")
    partitions, unique_ids = [], set()
    for i in range(count):
        entry = table[i*entry_size:(i+1)*entry_size]
        if entry[:16] == bytes(16):
            continue
        start, end = struct.unpack_from("<QQ", entry, 32)
        if not first <= start <= end <= last or entry[16:32] == bytes(16) or entry[16:32] in unique_ids:
            raise ValueError("GPT partition bounds/identity")
        if any(start <= b and a <= end for a, b in partitions):
            raise ValueError("GPT partition overlap")
        unique_ids.add(entry[16:32])
        partitions.append((start, end))
    return partitions


def image_gate(payload, expected_sha256, signature, verifier=None):
    """A negative-path gate, NOT a cryptographic implementation.

    A real audited verifier is absent; default rejection is unconditional.
    Test-only callbacks must never be wired into a production boot path.
    """
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        return False
    if verifier is None:
        return False
    return bool(verifier(payload, signature))


def memory_report(regions):
    """Count disjoint owned physical regions; reject overlap / unsigned overflow.

    Includes reservations, not merely touched bytes. Aliases must be recorded by
    reference, not as additional regions. Fixture measurements are not device RAM.
    """
    ordered = sorted(regions, key=lambda r: r["start"])
    total, end = 0, 0
    categories = {}
    for region in ordered:
        start, size = region["start"], region["size"]
        if (type(start) is not int or type(size) is not int or start < end or start < 0
                or size <= 0 or start + size > 2**64):
            raise ValueError("memory bounds or overlap")
        total += size
        end = start + size
        category = region["category"]
        categories[category] = categories.get(category, 0) + size
    return {"owned_bytes": total, "limit_bytes": 104_857_600,
            "below_target": total < 104_857_600, "categories": categories,
            "scope": "HOST_FIXTURE_NOT_DEVICE_MEASUREMENT"}
