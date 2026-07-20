import unittest
import restem

class BenchmarkTest(unittest.TestCase):
    def test_research_method_clears_baseline(self):
        result = restem.run()
        self.assertGreaterEqual(result["snr_gain_db"], 3)

if __name__ == "__main__":
    unittest.main()
