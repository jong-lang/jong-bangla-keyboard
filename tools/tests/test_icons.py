"""Supplied artwork dimensions, self-contained SVGs and exact package paths."""

from pathlib import Path
from html.parser import HTMLParser
import struct
import unittest
import xml.etree.ElementTree as ET

from tools.icon_payload import ICON_PATHS


ROOT = Path(__file__).resolve().parents[2]


class ArtworkTests(unittest.TestCase):
    def test_readme_picture_selects_both_appearances_with_accessible_fallback(self):
        class Picture(HTMLParser):
            def __init__(self):
                super().__init__()
                self.elements = []

            def handle_starttag(self, tag, attrs):
                if tag in {"source", "img"}:
                    self.elements.append((tag, dict(attrs)))

        parser = Picture()
        parser.feed((ROOT / "README.md").read_text())
        sources = [attrs for tag, attrs in parser.elements if tag == "source"]
        self.assertEqual({a["media"]: a["srcset"] for a in sources}, {
            "(prefers-color-scheme: dark)": "assets/logo/logo-tagline-dark.svg",
            "(prefers-color-scheme: light)": "assets/logo/logo-tagline-light.svg",
        })
        fallback, = [attrs for tag, attrs in parser.elements if tag == "img"]
        self.assertEqual(fallback["src"], "assets/logo/logo-tagline-light.svg")
        self.assertIn("Jong Bangla Keyboard", fallback["alt"])
        self.assertEqual(fallback["width"], "540")
        for source in sources:
            self.assertTrue((ROOT / source["srcset"]).is_file())

    def test_png_exports_have_actual_dimensions_and_alpha(self):
        exports = {
            "app-icon/app-icon-light-128px.png": (128, 128),
            "app-icon/app-icon-light-256px.png": (256, 256),
            "app-icon/app-icon-light-512px.png": (512, 512),
            "tray-icon/icon-tray-linux-light-24px.png": (24, 19),
            "tray-icon/icon-tray-linux-dark-24px.png": (24, 19),
        }
        for name, dimensions in exports.items():
            with self.subTest(name=name):
                data = (ROOT / "assets" / name).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(data[12:16], b"IHDR")
                self.assertEqual(struct.unpack(">II", data[16:24]), dimensions)
                self.assertEqual(data[24:26], bytes((8, 6)))  # 8-bit RGBA

    def test_svgs_are_self_contained_paths_with_the_expected_background_ink(self):
        names = [*(ROOT / "assets/logo").glob("*.svg"),
                 *(ROOT / "assets/app-icon").glob("*.svg"),
                 *(ROOT / "assets/tray-icon").glob("*linux*.svg")]
        self.assertEqual(len(names), 7)
        for path in names:
            with self.subTest(name=path.name):
                svg = ET.fromstring(path.read_bytes())
                self.assertEqual(svg.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertEqual(len(svg.attrib["viewBox"].split()), 4)
                self.assertTrue(any(node.tag.endswith("}path") for node in svg.iter()))
                for node in svg.iter():
                    self.assertIn(node.tag.rsplit("}", 1)[-1],
                                  {"svg", "defs", "style", "title", "g", "path", "rect", "polygon"})
                    self.assertFalse(any("href" in key for key in node.attrib))
                style = "".join(svg.itertext())
                self.assertNotIn("url(", style)
                self.assertNotIn("@import", style)
                ink = "#fdfcfd" if "dark" in path.name else "#24282b"
                self.assertIn(ink, style)

    def test_icon_allowlist_and_rpm_manifest_are_exact(self):
        # Independent path inventory: catch accidental omissions/extra payload.
        expected = {
            "scalable/apps/jong-bangla.svg",
            "128x128/apps/jong-bangla.png", "256x256/apps/jong-bangla.png",
            "512x512/apps/jong-bangla.png",
            "scalable/status/jong-symbolic.svg",
            "scalable/status/fcitx-jong-bangla-light.svg",
            "scalable/status/fcitx-jong-bangla-dark.svg",
            "24x24/status/fcitx-jong-bangla-light.png",
            "24x24/status/fcitx-jong-bangla-dark.png",
        }
        self.assertEqual(set(ICON_PATHS), {f"icons/hicolor/{p}" for p in expected})
        self.assertEqual(len(ICON_PATHS), len(expected))
        spec = (ROOT / "packaging/fedora/jong-bangla.spec.in").read_text()
        actual = {line.removeprefix("%{_datadir}/") for line in spec.splitlines()
                  if line.startswith("%{_datadir}/icons/")}
        self.assertEqual(actual, set(ICON_PATHS))


if __name__ == "__main__":
    unittest.main()
