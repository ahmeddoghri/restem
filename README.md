# restem

**Multi-step music source separation that improves a separator without retraining it.**

Most "better separation" pitches mean bigger model, more data, another training run. restem doesn't touch a single weight. It takes whatever a separator already produced, looks at how much of the *other* source is still leaking through, and subtracts a little more of it — then does that again, and again, until the leakage stops moving. Same separator, same weights, just refusing to stop after one pass when the estimate obviously isn't done improving.

It's a compact, inspectable implementation inspired by [the 2025 training-free multi-step audio source separation method](https://arxiv.org/abs/2505.19534), rebuilt small enough to read in one sitting and run without a GPU, a checkpoint, or an API key.

## The result

```bash
python restem.py
```
```json
{
  "one_step_snr_db": 8.78,
  "multi_step_snr_db": 36.52,
  "snr_gain_db": 27.74,
  "steps": 5
}
```

One pass of naive separation gets a vocal estimate to 8.78 dB SNR against the clean source — audible, but the backing track is still bleeding through. Five iterative refinement passes, each subtracting the estimated leakage of the interfering basis signal, push that to 36.52 dB — a 27.74 dB gain, with zero retraining and zero new parameters.

**Update:** "the known backing-signal basis" was known to a fault — the
projection basis is the exact 440 Hz frequency of the synthetic backing
tone, hardcoded. A mismatch of even 0.5 Hz between the assumed and true
frequency collapses the entire 27.74 dB gain to 0.00 dB. `restem_v2.py`
estimates the interferer's frequency from the observable mixture instead
of assuming it, and holds a real ~20 dB mean gain across dozens of
frequencies the original code was never told about. Details below.

## How it works

A synthetic mixture is built from a clean "vocal" tone and a "backing" tone at different frequencies. The one-step estimate is a naive separation that still contains real leakage from the backing signal. Each refinement step projects the current estimate onto the known backing-signal basis, measures how much leakage remains, and subtracts a fraction of it — a simple iterative leakage-cancellation loop, five steps deep. It writes both `mixture.wav` and `separated.wav` to `demo/` so you can actually listen to before and after instead of taking a metric's word for it.

## Run it

```bash
python restem.py
python -m unittest discover -s tests -v
```

The benchmark writes its result to stdout and two playable WAV files to `demo/`.

## What is tested

The test compares the multi-step estimate against the one-step baseline and requires `snr_gain_db >= 3`. The data generator is deterministic, so the number in this README, in CI, and in the portfolio case study are the same number, not three different ones that happen to rhyme.

## Scope

This is an educational research reproduction on a controlled synthetic two-tone mixture, not real multi-instrument audio. It is not a clinical, diagnostic, production audio-production, or safety-critical system. The point is to make one mechanism — iterative training-free refinement beats a single separation pass — measurable and audible without hiding it behind a checkpoint.

## The "known" basis was known to fractions of a Hz

`restem.py`'s refinement loop projects onto
`basis=[math.sin(2*math.pi*440*t/RATE) ...]` — the exact frequency of the
synthetic backing tone, with no noise and no estimation. Checked directly:
assume the interferer is at 439.5 Hz instead of the true 440.0 Hz (a 0.5 Hz
error, well within what any real frequency estimate would carry) and the
gain collapses from 27.74 dB to 0.00 dB. Given more iterations at the
*exact* frequency, SNR keeps climbing past 150 dB — a deterministic linear
convergence given a perfectly known, perfectly orthogonal basis, not a
bounded "5 steps of refinement" result.

```bash
python eval_v2.py
```
```
tuning (40 seeds):  hardcoded_mean_gain_db=0.00   estimated_mean_gain_db=21.03   estimated_min_gain_db=14.96
holdout (30 seeds): hardcoded_mean_gain_db=0.00   estimated_mean_gain_db=20.45   estimated_min_gain_db=14.64
```

`restem_v2.py` replaces the hardcoded basis with a coarse-to-fine Goertzel
frequency search over the observable mixture itself (excluding a band
around the target's own known frequency) — a real, training-free
estimation step, not an assumption. Across 40 tuning and a disjoint 30-seed
holdout (evaluated once), each mapped to a different, non-integer
interferer frequency the original code never saw: the hardcoded basis
scores exactly 0.00 dB mean gain on every single seed (none happen to land
on exactly 440 Hz), while the estimated basis holds a real mean gain of
~20-21 dB, never below 14.6 dB. `restem.py` is untouched and the published
27.74 dB number still reproduces exactly. (Sources within ~40 Hz of the
target frequency are excluded from the adversarial sweep — near-unison
sources are a genuinely hard case for any frequency-domain separation
method, not specific to this fix.)

## Research basis

- [The 2025 training-free multi-step audio source separation method](https://arxiv.org/abs/2505.19534)
- Original implementation and benchmark in this repository are MIT licensed.

## License

MIT
