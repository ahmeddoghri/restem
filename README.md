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

## Research basis

- [The 2025 training-free multi-step audio source separation method](https://arxiv.org/abs/2505.19534)
- Original implementation and benchmark in this repository are MIT licensed.

## License

MIT
