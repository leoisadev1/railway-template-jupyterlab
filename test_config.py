import os
import runpy
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class ConfigTests(unittest.TestCase):
    def load(self, env):
        config = SimpleNamespace(
            IdentityProvider=SimpleNamespace(),
            PasswordIdentityProvider=SimpleNamespace(),
            ServerApp=SimpleNamespace(),
            FileContentsManager=SimpleNamespace(),
        )
        with patch.dict(os.environ, env, clear=True):
            runpy.run_path(
                str(Path(__file__).with_name("railway_server_config.py")),
                init_globals={"get_config": lambda: config},
            )
        return config

    def test_auth_and_default_port(self):
        config = self.load({"JUPYTER_TOKEN": "test-token"})
        self.assertEqual(config.IdentityProvider.token, "test-token")
        self.assertEqual(config.ServerApp.port, 8888)
        self.assertFalse(config.PasswordIdentityProvider.allow_password_change)
        self.assertFalse(hasattr(config.ServerApp, "allow_origin"))

    def test_custom_port(self):
        config = self.load({"JUPYTER_TOKEN": "test-token", "PORT": "4321"})
        self.assertEqual(config.ServerApp.port, 4321)
        self.assertEqual(config.ServerApp.port_retries, 0)

    def test_missing_or_blank_token(self):
        for token in ("", " "):
            with self.subTest(token=repr(token)), self.assertRaises(ValueError):
                self.load({"JUPYTER_TOKEN": token})

    def test_invalid_port(self):
        for port in ("0", "65536", "abc", ""):
            with self.subTest(port=port), self.assertRaises(ValueError):
                self.load({"JUPYTER_TOKEN": "test-token", "PORT": port})


if __name__ == "__main__":
    unittest.main()
