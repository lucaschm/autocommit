import unittest
import git

class TestGit(unittest.TestCase):

    def test_hi(self):
        result = git.hi()
        self.assertEqual(result, "hi")

if __name__ == "__main__":
    unittest.main()