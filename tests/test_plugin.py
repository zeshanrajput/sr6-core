"""
Unit tests for Antigravity Agent Plugin management in sr6core.plugin.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from sr6core.plugin import (
    get_plugin_source_dir,
    get_plugin_manifest,
    get_plugin_status,
    configure_repo_plugin_inheritance,
)


class TestPluginManagement(unittest.TestCase):
    def test_plugin_source_exists_and_valid(self):
        source_dir = get_plugin_source_dir()
        self.assertTrue(source_dir.exists(), f"Source dir {source_dir} should exist")

        manifest = get_plugin_manifest(source_dir)
        self.assertIsNotNone(manifest, "Manifest should be valid JSON")
        self.assertEqual(manifest.get("name"), "sr6-narrative-suite")
        self.assertEqual(manifest.get("version"), "1.0.0")

    def test_plugin_status_inspection(self):
        status = get_plugin_status()
        self.assertTrue(status["source_exists"])
        self.assertEqual(status["source_version"], "1.0.0")
        self.assertEqual(status["skills_count"], 8)
        self.assertIn("global_installed", status)

    def test_configure_repo_plugin_inheritance(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            ok, msg = configure_repo_plugin_inheritance(str(repo_path))
            self.assertTrue(ok)
            plugins_json = repo_path / ".agents" / "plugins.json"
            self.assertTrue(plugins_json.exists())

            with open(plugins_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertIn("inherits", data)
            self.assertGreaterEqual(len(data["inherits"]), 1)
            self.assertIn("path", data["inherits"][0])


if __name__ == "__main__":
    unittest.main()
