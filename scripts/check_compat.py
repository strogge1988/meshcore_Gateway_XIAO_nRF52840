#!/usr/bin/env python3
"""Fail closed on missing upstream APIs; no attempt to guess a new MeshCore layout."""
from pathlib import Path
import sys

f = Path(sys.argv[1]) if len(sys.argv)>1 else Path('firmware')
checks = {
    'platformio.ini': ('platformio.local.ini',),
    'variants/xiao_nrf52/platformio.ini': ('[env:Xiao_nrf52_repeater]', 'D6', 'D7'),
    'examples/simple_repeater/main.cpp': ('void setup()', 'void loop()', 'the_mesh.begin(fs);', '  the_mesh.loop();'),
    'src/helpers/bridges/RS232Bridge.cpp': ('RS232Bridge::begin()', 'RS232Bridge::sendPacket'),
}
for path, anchors in checks.items():
    src=f/path
    if not src.is_file():
        raise SystemExit(f'Unsupported upstream: missing {path}')
    txt=src.read_text(encoding='utf-8')
    for key in anchors:
        if key not in txt:
            raise SystemExit(f'Unsupported upstream: {path} missing anchor {key!r}')
print('Upstream structural compatibility checks: OK')
