import unittest
from unittest.mock import patch
import os
from pathlib import Path

import util


class TestUtil(unittest.TestCase):

    @patch('util.main_folders', ['src/', 'app/'])
    @patch('util.main_extensions', ['.py', '.js'])
    def test_is_main_file(self):
        self.assertTrue(util.is_main_file('src/main.py'))
        self.assertTrue(util.is_main_file('app/util.js'))
        self.assertFalse(util.is_main_file('lib/main.txt'))
        self.assertFalse(util.is_main_file('src/notes.md'))

    @patch('util.attachment_folders', ['attachments/', 'assets/'])
    @patch('util.attachment_extensions', ['.png', '.jpg', '.pdf'])
    def test_is_attachment_file(self):
        self.assertTrue(util.is_attachment_file('attachments/image.png'))
        self.assertTrue(util.is_attachment_file('assets/manual.pdf'))
        self.assertTrue(util.is_attachment_file('docs/overview.jpg'))
        self.assertFalse(util.is_attachment_file('src/main.py'))

    @patch('util.repo_path', '/home/user/project')
    @patch('util.excluded_dirs', ['build/', 'venv/'])
    def test_ignore_path(self):
        self.assertTrue(util.ignore_path('/home/user/project/build/temp.py'))
        self.assertTrue(util.ignore_path('/home/user/project/venv/lib/module.py'))
        self.assertFalse(util.ignore_path('/home/user/project/src/main.py'))

    def test_file_exists(self):
        # Create a temp file and test its existence
        test_file = 'temp_test_file.txt'
        with open(test_file, 'w') as f:
            f.write("Hello")

        self.assertTrue(util.file_exists(test_file))

        os.remove(test_file)
        self.assertFalse(util.file_exists(test_file))


if __name__ == '__main__':
    unittest.main()
