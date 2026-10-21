"""Strict extraction of target-compiler XNU genassym metadata (MIT).

Only the -fno-integrated-as decimal .ascii representation is supported.
Unknown compiler representations fail rather than inventing offsets.
"""
import re

MARKER = 'DEFINITION__define__'
DEFINITION = re.compile(r'\s*DEFINITION__define__([A-Za-z_][A-Za-z0-9_]*):\s*'
                        r'\.ascii\s+"([#$]?-?[0-9]+)"\s*')


def parse_assym(assembly, required=()):
    if not isinstance(assembly, str) or len(assembly) > 2 * 1024 * 1024:
        raise ValueError('Invalid or oversized compiler metadata')
    result = {}
    for line in assembly.splitlines():
        if MARKER not in line:
            continue
        match = DEFINITION.fullmatch(line)
        if not match:
            raise ValueError('Unsupported genassym representation: '+line[:160])
        key, literal = match.groups()
        value = int(literal.removeprefix('#').removeprefix('$'))
        if key in result or not -(1 << 63) <= value < (1 << 64):
            raise ValueError('Duplicate or out-of-range genassym definition: '+key)
        result[key] = value
    if not result or not set(required).issubset(result):
        raise ValueError('Missing required genassym definitions')
    if set(result) & {name+'_NUM' for name in result}:
        raise ValueError('genassym numeric alias collides with another definition')
    return result


def render_assym(values, *, prefix=''):
    if prefix and not re.fullmatch('[A-Z_]+', prefix):
        raise ValueError('Invalid metadata namespace')
    lines = ['/* Generated from real XNU ARM64 layouts; do not edit. */']
    for key, value in values.items():
        lines += [f'#define {prefix}{key} {value}', f'#define {prefix}{key}_NUM {value}']
    return '\n'.join(lines)+'\n'
