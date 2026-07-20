# restem

**Multi-step music source separation that improves a separator without retraining it.**

restem is a compact, inspectable implementation inspired by [The 2025 training-free multi-step audio source separation method.](https://arxiv.org/abs/2505.19534).
It turns the paper's core idea into a deterministic benchmark that runs on a laptop with Python's standard library.

## Run it

```bash
python restem.py
python -m unittest discover -s tests -v
```

The benchmark writes its result to stdout. Audio projects also write playable WAV files to `demo/`.

## What is tested

The test compares the research-inspired method with a deliberately legible baseline and requires
`snr_gain_db >= 3`. The data generator is seeded, so the number in this README,
CI, and the portfolio case study can be reproduced.

## Scope

This is an educational research reproduction on controlled synthetic data. It is not a clinical,
diagnostic, production genomics, copyright-authentication, or safety-critical system. The point is
to make one mechanism measurable without hiding it behind a checkpoint or API.

## Research basis

- [The 2025 training-free multi-step audio source separation method.](https://arxiv.org/abs/2505.19534)
- Original implementation and benchmark in this repository are MIT licensed.

## License

MIT

## Reproduced result

| Metric | Value |
|---|---:|
| `one_step_snr_db` | **8.78** |
| `multi_step_snr_db` | **36.52** |
| `snr_gain_db` | **27.74** |
| `steps` | **5** |
