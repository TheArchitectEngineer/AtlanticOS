"""Validate evidence hashes and minimum provenance; not authenticity of hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def validate(path):
    path = Path(path).resolve()
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1:
        raise ValueError('unsupported evidence schema')
    label = data.get('label')
    if label not in {'HOST_TESTED','EMULATED','BUILT_ARM64','DEVICE_VERIFIED'}:
        raise ValueError('unknown evidence label')
    if not data.get('scope') or not data.get('artifacts'):
        raise ValueError('scope/artifacts required')
    if label == 'DEVICE_VERIFIED':
        for key in ('board_id','firmware_id','binary_sha256','physical_capture_sha256','android_recovery_result','timestamp'):
            if not data.get(key):
                raise ValueError(f'device record missing {key}')
        for key in ('binary_sha256','physical_capture_sha256'):
            if not re.fullmatch('[0-9a-f]{64}', data[key]):
                raise ValueError('invalid device digest')
    root = path.parent
    seen = set()
    for record in data['artifacts']:
        relative = record['path']
        source = (root/relative).resolve()
        if source == path or not source.is_relative_to(root) or not source.is_file() or relative in seen:
            raise ValueError('invalid, duplicate or escaping artifact path')
        seen.add(relative)
        if hashlib.sha256(source.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError(f'hash mismatch: {relative}')
    if label == 'DEVICE_VERIFIED':
        for role, field in [('binary','binary_sha256'),('physical_capture','physical_capture_sha256')]:
            if not any(a.get('role') == role and a['sha256'] == data[field] for a in data['artifacts']):
                raise ValueError(f'missing hashed {role} artifact')
    return len(seen)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    args = parser.parse_args()
    print(f'PASS: {validate(args.manifest)} evidence artifacts; physical authenticity requires review')
