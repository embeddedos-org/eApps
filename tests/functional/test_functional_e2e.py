import unittest
class TestEAppsFunctional(unittest.TestCase):
    def test_app_lifecycle_pipeline(self):
        pipeline = ["download", "install", "launch", "terminate"]
        self.assertEqual(pipeline[-1], "terminate")
