"""Adversarial interferer frequencies for the estimated-basis fix.

restem.py hardcodes the interferer's exact frequency (440 Hz) into its
projection basis. TUNING_SEEDS/HOLDOUT_SEEDS each map to a different,
non-integer interferer frequency (via a seeded RNG), used to check whether
restem_v2.py's Goertzel-based frequency estimation generalizes to
interferers the original code was never told about.

Frequencies are sampled at least 40 Hz away from the target's own 220 Hz,
since sources that close in frequency are a fundamentally hard case for
any frequency-domain separation method, not specific to this fix -- see
the README for that caveat.

TUNING_SEEDS: used to characterize the estimation approach.
HOLDOUT_SEEDS: disjoint, evaluated exactly once after characterization.
"""
import random

TARGET_FREQ = 220.0
MIN_SEPARATION_HZ = 40.0


def interferer_freq_for_seed(seed: int) -> float:
    rng = random.Random(seed)
    while True:
        freq = rng.uniform(100.0, 900.0)
        if abs(freq - TARGET_FREQ) >= MIN_SEPARATION_HZ:
            return freq


TUNING_SEEDS = list(range(1, 41))
HOLDOUT_SEEDS = list(range(1000, 1030))
