import unittest
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
class RecipeTests(unittest.TestCase):
  def test_layout(self):
    for path in ['platformio.local.ini','scripts/resolve_version.sh','scripts/check_compat.py','.github/workflows/build.yml']:
      self.assertTrue((ROOT/path).is_file(),path)
  def test_uart(self):
    cfg=(ROOT/'platformio.local.ini').read_text()
    self.assertIn('WITH_RS232_BRIDGE=Serial1',cfg)
    self.assertIn('WITH_RS232_BRIDGE_TX=D6',cfg)
    self.assertIn('WITH_RS232_BRIDGE_RX=D7',cfg)
    if 'XIAO_GATEWAY_EXTRAS' in cfg:
      self.assertLess(cfg.index('XIAO_GATEWAY_EXTRAS'), cfg.index('build_src_filter ='))
  def test_upstream_versions(self):
    src=(ROOT/'scripts/resolve_version.sh').read_text()
    self.assertIn('repeater-v',src)
    self.assertIn('sort -V',src)
  def test_workflow(self):
    txt=(ROOT/'.github/workflows/build.yml').read_text()
    self.assertNotIn('path: recipe',txt)
    self.assertIn('inputs.meshcore_version',txt)
    self.assertIn('firmware.uf2',txt)
    self.assertIn('cp platformio.local.ini firmware/platformio.local.ini',txt)
