import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from autocommit.note_handler import NoteHandler

class TestNoteHandler(unittest.TestCase):

    # expect Error, when constructor is called without "repo_path" parameter
    def test_constructor_without_parameter_raises_error(self):
        with self.assertRaises(TypeError):
            NoteHandler()  # Missing the required string argument

if __name__ == "__main__":
    unittest.main()