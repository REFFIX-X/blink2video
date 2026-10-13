"""The live dashboard count reports the number of cameras and armed cameras."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


class TestsDetectionCount(unittest.TestCase):
    def test_count_is_english_and_camera_count_is_pluralized(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node introuvable")
        source = Path(__file__).with_name("serve_app.js").read_text(encoding="utf-8")
        patterns = [r"^const I18N = \{.*?^\};", r"^function t\(k\) \{[^\n]*\}$",
                    r"^function tf\(k, v\) \{.*?^\}", r"^function renderLive\(\) \{.*?^\}"]
        code = "\n".join(re.search(p, source, re.M | re.S).group(0) for p in patterns)
        for cameras, expected in (([{"armed": True}, {"armed": True}, {"armed": False}],
                                   "3 cameras · 2 armed"),
                                  ([{"armed": True}], "1 camera · 1 armed")):
            for system_armed in (False, True):
                with self.subTest(expected=expected, system_armed=system_armed):
                    systems = [{"name": "Test", "key": "test", "armed": system_armed,
                                "cameras": cameras}]
                    script = ("let _lang = \"fr\"; let system = {systems: "
                              + json.dumps(systems) + "}; let rafraichirVignettes = false; "
                              "const elements = {count: {}, list: {}}; const $ = k => elements[k]; "
                              "const nomsDirectsActifs = () => []; const h = v => v; "
                              "const cameraCard = () => ''; const estMasquee = () => false; const comparerNoms = (a, b) => String(a).localeCompare(String(b));\n" + code +
                              "\nrenderLive(); console.log(JSON.stringify(elements.count.textContent));")
                    result = subprocess.run([node, "-"], input=script, capture_output=True,
                                            text=True, encoding="utf-8", check=True)
                    self.assertEqual(json.loads(result.stdout), expected)
