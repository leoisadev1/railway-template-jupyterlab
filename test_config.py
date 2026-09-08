import os
import runpy
import subprocess
import tempfile
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


class StartupTests(unittest.TestCase):
    def run_wrapper(self, uid, **extra):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stubs = {
                "id": '#!/bin/bash\nprintf "%s\\n" "$TEST_UID"\n',
                "start.sh": '#!/bin/bash\nprintf "drop-user %s\\n" "$*"\n',
                "start-notebook.py": '#!/bin/bash\nprintf "notebook %s\\n" "$*"\n',
            }
            for name, contents in stubs.items():
                path = root / name
                path.write_text(contents)
                path.chmod(0o755)
            env = {"PATH": str(root), "TEST_UID": str(uid),
                   "JUPYTER_TOKEN": "private-test-value", **extra}
            return subprocess.run(
                ["/bin/bash", str(Path(__file__).with_name("railway-start.sh"))],
                env=env, capture_output=True, text=True, timeout=5,
            )

    def test_root_uses_upstream_user_switch(self):
        result = self.run_wrapper(0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("drop-user start-notebook.py --config=", result.stdout)
        self.assertNotIn("private-test-value", result.stdout + result.stderr)

    def test_nonroot_starts_directly(self):
        result = self.run_wrapper(1000)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("notebook --config=", result.stdout)
        self.assertNotIn("private-test-value", result.stdout + result.stderr)

    def test_root_notebook_user_rejected(self):
        result = self.run_wrapper(0, NB_UID="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unprivileged", result.stderr)

    def test_missing_token_rejected_before_start(self):
        result = self.run_wrapper(1000, JUPYTER_TOKEN="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required", result.stderr)


if __name__ == "__main__":
    unittest.main()
