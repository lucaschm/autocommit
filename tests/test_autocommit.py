import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
import os
import subprocess
from pathlib import Path


# setup will be performed before each test and teardown will be performed
# after each test. This means every test starts with a new fresh setup.
class TestGitIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the test Git repo
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_path = Path(self.temp_dir.name)
        print("You can inspect the temporary directory with this command (as long as cleanup was not performed):")
        print("cd ", self.repo_path)


        # Initialize a Git repo
        subprocess.run(['git', 'init', '--initial-branch=main'], cwd=self.repo_path, check=True)

        # Create a test file
        self.test_file = self.repo_path / "test.txt"
        self.test_file.write_text("Hello, Git!")

        # Add and commit the test file
        subprocess.run(['git', 'add', 'test.txt'], cwd=self.repo_path, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.repo_path, check=True)

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_commit(self):
        # Simulate a change
        self.test_file.write_text("Modified content")
        subprocess.run(['git', 'add', 'test.txt'], cwd=self.repo_path, check=True)
        subprocess.run(['git', 'commit', '-m', 'Modify file'], cwd=self.repo_path, check=True)

        # Check log to verify commit
        result = subprocess.run(['git', 'log', '--oneline'], cwd=self.repo_path, capture_output=True, text=True)
        self.assertIn("Modify file", result.stdout)

    def test_2(self):
        # Simulate a change
        text = self.test_file.read_text()
        self.test_file.write_text(text + "\n new line from test_2")
        subprocess.run(['git', 'add', 'test.txt'], cwd=self.repo_path, check=True)
        subprocess.run(['git', 'commit', '-m', 'Modify file'], cwd=self.repo_path, check=True)

        # Check log to verify commit
        result = subprocess.run(['git', 'log', '--oneline'], cwd=self.repo_path, capture_output=True, text=True)
        self.assertIn("Modify file", result.stdout)

if __name__ == "__main__":
    unittest.main()
