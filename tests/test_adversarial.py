import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import restem
from adversarial import HOLDOUT_SEEDS, TUNING_SEEDS, interferer_freq_for_seed
from eval_v2 import summarize
from restem_v2 import run, run_hardcoded_basis


class AdversarialTest(unittest.TestCase):
    def test_holdout_disjoint_from_tuning(self):
        self.assertTrue(set(TUNING_SEEDS).isdisjoint(HOLDOUT_SEEDS))

    def test_original_benchmark_still_reproduces_exactly(self):
        result = restem.run()
        self.assertEqual(result["one_step_snr_db"], 8.78)
        self.assertEqual(result["multi_step_snr_db"], 36.52)
        self.assertEqual(result["snr_gain_db"], 27.74)

    def test_v2_hardcoded_baseline_matches_original_module_at_published_frequency(self):
        result = run_hardcoded_basis()
        self.assertEqual(result["one_step_snr_db"], 8.78)
        self.assertEqual(result["multi_step_snr_db"], 36.52)
        self.assertEqual(result["snr_gain_db"], 27.74)

    def test_original_bug_hardcoded_basis_collapses_with_a_fraction_of_a_hz_mismatch(self):
        """restem.py's basis assumes the interferer is at EXACTLY 440 Hz.
        A 0.5 Hz mismatch (well within realistic frequency-estimation
        error for any real source) collapses the gain to 0.0 dB."""
        result = run_hardcoded_basis(interferer_freq=439.5)
        self.assertEqual(result["snr_gain_db"], 0.0)

    def test_original_bug_hardcoded_basis_gives_zero_gain_across_varied_frequencies(self):
        gains = [run_hardcoded_basis(interferer_freq=interferer_freq_for_seed(s))["snr_gain_db"] for s in TUNING_SEEDS]
        self.assertEqual(set(gains), {0.0})

    def test_more_iterations_at_the_exact_frequency_diverge_far_past_the_published_number(self):
        """Given the noiseless, exactly-known synthetic basis, the loop is a
        deterministic convergent linear operation, not a bounded 5-step
        result: more iterations climb well past the published 36.52 dB."""
        from restem_v2 import RATE, snr
        import math
        n = RATE
        vocal = [.75 * math.sin(2 * math.pi * 220 * t / RATE) for t in range(n)]
        backing = [.65 * math.sin(2 * math.pi * 440 * t / RATE) for t in range(n)]
        basis = [math.sin(2 * math.pi * 440 * t / RATE) for t in range(n)]
        est = [a + .42 * b for a, b in zip(vocal, backing)]
        for _ in range(30):
            leakage = sum(e * b for e, b in zip(est, basis)) / sum(b * b for b in basis)
            est = [e - .55 * leakage * b for e, b in zip(est, basis)]
        self.assertGreater(snr(vocal, est), 100)

    def test_v2_fix_generalizes_on_tuning_seeds(self):
        result = summarize(TUNING_SEEDS)
        self.assertEqual(result["hardcoded_mean_gain_db"], 0.0)
        self.assertGreater(result["estimated_min_gain_db"], 10)

    def test_v2_fix_generalizes_on_frozen_holdout_seeds(self):
        result = summarize(HOLDOUT_SEEDS)
        self.assertEqual(result["hardcoded_mean_gain_db"], 0.0)
        self.assertGreater(result["estimated_min_gain_db"], 10)

    def test_v2_does_not_regress_the_original_published_frequency(self):
        result = run(interferer_freq=440.0)
        self.assertEqual(result["snr_gain_db"], 27.74)
        self.assertAlmostEqual(result["estimated_interferer_freq"], 440.0, delta=0.5)

    def test_original_module_untouched(self):
        import inspect

        source = inspect.getsource(restem.run)
        self.assertIn("basis=[math.sin(2*math.pi*440*t/RATE)", source)

    def test_report_is_reproducible(self):
        a = summarize(TUNING_SEEDS[:5])
        b = summarize(TUNING_SEEDS[:5])
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
