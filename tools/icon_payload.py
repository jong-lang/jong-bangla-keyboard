"""Exact icon paths shared by staged, release and package verification."""

from pathlib import Path


# Relative to the data directory, normally /usr/share. Keep this allowlist exact.
ICON_PATHS = (
    "icons/hicolor/scalable/apps/jong-bangla.svg",
    "icons/hicolor/128x128/apps/jong-bangla.png",
    "icons/hicolor/256x256/apps/jong-bangla.png",
    "icons/hicolor/512x512/apps/jong-bangla.png",
    "icons/hicolor/scalable/status/jong-symbolic.svg",
    "icons/hicolor/scalable/status/fcitx-jong-bangla-light.svg",
    "icons/hicolor/scalable/status/fcitx-jong-bangla-dark.svg",
    "icons/hicolor/24x24/status/fcitx-jong-bangla-light.png",
    "icons/hicolor/24x24/status/fcitx-jong-bangla-dark.png",
)


def icon_files(data_dir):
    return {Path(data_dir) / name for name in ICON_PATHS}
