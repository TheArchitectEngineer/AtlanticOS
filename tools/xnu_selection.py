"""Read generated Mach/device C source selection from the official config tool."""
import re


def generated_cfiles(text):
    flat = text.replace('\\\n', ' ')
    matches = re.findall(r'^CFILES\s*=\s*([^\n]+)', flat, re.M)
    if len(matches) != 1:
        raise ValueError('Expected exactly one native CFILES assignment')
    selected = []
    for name in matches[0].split():
        if not name.startswith(('./mach/', './device/')):
            continue
        if not re.fullmatch(r'\./(?:mach|device)/[A-Za-z0-9_]+\.c', name):
            raise ValueError('Unexpected generated Mach/device source path: '+name)
        selected.append(name.removeprefix('./'))
    if not selected or len(selected) != len(set(selected)):
        raise ValueError('Empty or duplicate native generated-source selection')
    return selected
