import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
import shutil
import os
import subprocess
from pathlib import Path

from autocommit.git import get_repo_root

class TestGetRepoRoot(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.sub_temp_dir = str(Path(self.temp_dir) / "level1" / "level2")
        os.makedirs(self.sub_temp_dir)

        
        # Initialize a git repo in temp_dir
        subprocess.run(['git', 'init'], cwd=self.temp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tearDown(self):
        # Clean up after each test
        shutil.rmtree(self.temp_dir)

    def test_file_as_path(self):
        # Create a test file
        test_file = Path(self.sub_temp_dir) / "test.txt"
        test_file.write_text("Some text content.")

        repo_root = get_repo_root(test_file)
        self.assertEqual(repo_root, self.temp_dir)

    def test_dir_as_path(self):
        repo_root = get_repo_root(self.sub_temp_dir)
        self.assertEqual(repo_root, self.temp_dir)
    
    def test_wrong_parameter(self):
        with self.assertRaises(ValueError):
            get_repo_root("not a valid path")
        
        with self.assertRaises(ValueError):
            wrong_file = str(Path(self.temp_dir) / "non-existing-file.txt")
            get_repo_root(wrong_file)

        with self.assertRaises(ValueError):
            wrong_dir = str(Path(self.temp_dir) / "non-existing-directory")
            get_repo_root(wrong_dir)

    def test_path_is_no_git_repo(self):
        no_git_dir = tempfile.mkdtemp()
        with self.assertRaises(ValueError):
            get_repo_root(no_git_dir)

if __name__ == '__main__':
    unittest.main()
