"""Estimated-basis iterative refinement, as a parallel non-destructive fix.

restem.py's refinement loop projects the estimate onto
`basis=[sin(2*pi*440*t/RATE) ...]` -- the exact, noiseless frequency of the
synthetic backing tone, known to fractions of a Hz. Verified directly: if
the assumed basis frequency is off by even 0.5 Hz from the true 440 Hz, the
SNR gain collapses from 27.74 dB to essentially 0.00 dB. Given more
iterations at the exact frequency, SNR climbs past 150 dB (a deterministic
linear-algebra convergence, not a bounded "5 steps of refinement" result).
Neither behavior would survive contact with a real separator, which never
knows an interfering source's frequency to that precision.

This module estimates the interfering source's dominant frequency directly
from the observable mixture (via a coarse-to-fine Goertzel search,
excluding a band around the already-known target frequency), then uses
that estimate -- not a hardcoded oracle value -- as the projection basis
for the same iterative subtraction loop.
"""
import json
import math
import struct
import wave
from pathlib import Path

RATE = 8000


def snr(clean, estimate):
    signal = sum(x * x for x in clean)
    noise = sum((a - b) ** 2 for a, b in zip(clean, estimate))
    return 10 * math.log10(signal / max(noise, 1e-12))


def _goertzel_power(x, freq, rate):
    w = 2 * math.pi * freq / rate
    coeff = 2 * math.cos(w)
    s1 = s2 = 0.0
    for sample in x:
        s0 = sample + coeff * s1 - s2
        s2, s1 = s1, s0
    return s1 * s1 + s2 * s2 - coeff * s1 * s2


def estimate_dominant_freq(x, rate, exclude_freq, exclude_width=15.0, lo=60.0, hi=1200.0,
                            coarse_step=5.0, fine_step=0.1, fine_span=6.0):
    """Coarse-to-fine Goertzel search for the strongest frequency in `x`,
    excluding a band around `exclude_freq` (the target's own frequency)."""
    best_f, best_p = lo, -1.0
    f = lo
    while f <= hi:
        if abs(f - exclude_freq) > exclude_width:
            p = _goertzel_power(x, f, rate)
            if p > best_p:
                best_p, best_f = p, f
        f += coarse_step
    f = max(lo, best_f - fine_span)
    hi_f = min(hi, best_f + fine_span)
    best2_f, best2_p = best_f, -1.0
    while f <= hi_f:
        if abs(f - exclude_freq) > exclude_width:
            p = _goertzel_power(x, f, rate)
            if p > best2_p:
                best2_p, best2_f = p, f
        f += fine_step
    return best2_f


def run_hardcoded_basis(target_freq=220.0, interferer_freq=440.0, target_amp=.75,
                         interferer_amp=.65, leak=.42, assumed_basis_freq=440.0):
    """Same hardcoded-basis method as restem.py's run(), parameterized so it
    can be tested against interferer frequencies the basis wasn't told about."""
    n = RATE
    vocal = [target_amp * math.sin(2 * math.pi * target_freq * t / RATE) for t in range(n)]
    backing = [interferer_amp * math.sin(2 * math.pi * interferer_freq * t / RATE) for t in range(n)]
    estimate = [a + leak * b for a, b in zip(vocal, backing)]
    one = snr(vocal, estimate)
    basis = [math.sin(2 * math.pi * assumed_basis_freq * t / RATE) for t in range(n)]
    for _ in range(4):
        leakage = sum(e * b for e, b in zip(estimate, basis)) / sum(b * b for b in basis)
        estimate = [e - .55 * leakage * b for e, b in zip(estimate, basis)]
    multi = snr(vocal, estimate)
    return {
        "one_step_snr_db": round(one, 2),
        "multi_step_snr_db": round(multi, 2),
        "snr_gain_db": round(multi - one, 2),
        "steps": 5,
    }


def run(target_freq=220.0, interferer_freq=440.0, target_amp=.75, interferer_amp=.65, leak=.42):
    n = RATE
    vocal = [target_amp * math.sin(2 * math.pi * target_freq * t / RATE) for t in range(n)]
    backing = [interferer_amp * math.sin(2 * math.pi * interferer_freq * t / RATE) for t in range(n)]
    mixture = [a + b for a, b in zip(vocal, backing)]
    estimate = [a + leak * b for a, b in zip(vocal, backing)]
    one = snr(vocal, estimate)

    estimated_freq = estimate_dominant_freq(mixture, RATE, exclude_freq=target_freq)
    basis = [math.sin(2 * math.pi * estimated_freq * t / RATE) for t in range(n)]
    for _ in range(4):
        leakage = sum(e * b for e, b in zip(estimate, basis)) / sum(b * b for b in basis)
        estimate = [e - .55 * leakage * b for e, b in zip(estimate, basis)]
    multi = snr(vocal, estimate)

    return {
        "one_step_snr_db": round(one, 2),
        "multi_step_snr_db": round(multi, 2),
        "snr_gain_db": round(multi - one, 2),
        "steps": 5,
        "estimated_interferer_freq": round(estimated_freq, 2),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
