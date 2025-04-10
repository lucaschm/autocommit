import unittest
import tempfile
import shutil
import os
import subprocess
from git import is_git_repo

class TestIsGitRepo(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up after each test
        shutil.rmtree(self.temp_dir)

    def test_is_git_repo_true(self):
        # Initialize a git repo in temp_dir
        subprocess.run(['git', 'init'], cwd=self.temp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertTrue(is_git_repo(self.temp_dir))

    def test_is_git_repo_false(self):
        # temp_dir is not a git repo at first
        self.assertFalse(is_git_repo(self.temp_dir))

    def test_nonexistent_path(self):
        # Pass a path that doesn't exist
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent")
        self.assertFalse(is_git_repo(nonexistent_path))

if __name__ == '__main__':
    unittest.main()
