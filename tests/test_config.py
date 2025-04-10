import unittest
from unittest.mock import patch, mock_open
import builtins
import sys

# Patch sys.exit so it doesn't actually exit during tests
exit_patch = patch.object(sys, 'exit', side_effect=Exception("System exit"))

# Sample config data
mock_yaml_data = """
repo_path: "/home/user/project"
main_folders: ["src", "lib"]
main_extensions: [".py", ".js"]
attachment_folders: ["assets"]
attachment_extensions: [".jpg", ".png"]
excluded_dirs: [".git", "node_modules"]
"""

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Reset singleton before each test
        from config import Config
        Config._instance = None

    @patch("builtins.open", new_callable=mock_open, read_data=mock_yaml_data)
    @patch("yaml.safe_load", return_value={
        "repo_path": "/home/user/project",
        "main_folders": ["src", "lib"],
        "main_extensions": [".py", ".js"],
        "attachment_folders": ["assets"],
        "attachment_extensions": [".jpg", ".png"],
        "excluded_dirs": [".git", "node_modules"]
    })
    def test_config_values_loaded_correctly(self, mock_yaml, mock_file):
        from config import Config
        config = Config.get_instance()

        self.assertEqual(config.repo_path, "/home/user/project")
        self.assertEqual(config.main_folders, ["src", "lib"])
        self.assertEqual(config.main_extensions, [".py", ".js"])
        self.assertEqual(config.attachment_folders, ["assets"])
        self.assertEqual(config.attachment_extensions, [".jpg", ".png"])
        self.assertEqual(config.excluded_dirs, {".git", "node_modules"})

    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_missing_file_exits(self, mock_file):
        from config import Config
        with exit_patch:
            with self.assertRaises(Exception) as context:
                Config.get_instance()
            self.assertIn("System exit", str(context.exception))

    @patch("builtins.open", new_callable=mock_open, read_data=": invalid_yaml:")
    @patch("yaml.safe_load", side_effect=Exception("YAML parse error"))
    def test_yaml_error_exits(self, mock_yaml, mock_file):
        from config import Config
        with exit_patch:
            with self.assertRaises(Exception) as context:
                Config.get_instance()
            self.assertIn("System exit", str(context.exception))

    @patch("builtins.open", new_callable=mock_open, read_data=mock_yaml_data)
    @patch("yaml.safe_load", return_value={})
    def test_defaults_are_returned_if_keys_missing(self, mock_yaml, mock_file):
        from config import Config
        config = Config.get_instance()
        self.assertEqual(config.repo_path, ".")
        self.assertEqual(config.main_folders, [])
        self.assertEqual(config.main_extensions, [])
        self.assertEqual(config.attachment_folders, [])
        self.assertEqual(config.attachment_extensions, [])
        self.assertEqual(config.excluded_dirs, {".git", "venv", ".log"})

    @patch("pathlib.Path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=".DS_Store\nnode_modules/\n# comment\n\n.env")
    @patch("yaml.safe_load", return_value={"repo_path": "."})
    def test_gitignore_patterns_loaded(self, mock_yaml, mock_open_gitignore, mock_exists):
        from config import Config
        config = Config.get_instance()
        patterns = config.load_gitignore_patterns()
        self.assertEqual(patterns, [".DS_Store", "node_modules/", ".env"])

    def tearDown(self):
        from config import Config
        Config._instance = None  # Reset after each test

if __name__ == "__main__":
    unittest.main()
