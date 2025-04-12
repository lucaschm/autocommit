import unittest
from autocommit.note_handler import NoteHandler

class TestNoteHandler(unittest.TestCase):

    def test_constructor_missing_parameter(self):
        # expect Error, when constructor is called without "repo_path" parameter
        self.assertRaises(TypeError, NoteHandler())
    

if __name__ == "__main__":
    unittest.main()