"""Compare the hardcoded-basis method (restem.py's mechanism, parameterized)
to the estimated-basis fix (restem_v2.py) across many interferer
frequencies the original code was never told about."""
import json
import statistics as st

from adversarial import HOLDOUT_SEEDS, TUNING_SEEDS, interferer_freq_for_seed
from restem_v2 import run, run_hardcoded_basis


def summarize(seeds):
    hardcoded_gains = [run_hardcoded_basis(interferer_freq=interferer_freq_for_seed(s))["snr_gain_db"] for s in seeds]
    estimated_gains = [run(interferer_freq=interferer_freq_for_seed(s))["snr_gain_db"] for s in seeds]
    return {
        "n": len(seeds),
        "hardcoded_mean_gain_db": round(st.mean(hardcoded_gains), 2),
        "hardcoded_max_gain_db": max(hardcoded_gains),
        "estimated_mean_gain_db": round(st.mean(estimated_gains), 2),
        "estimated_min_gain_db": round(min(estimated_gains), 2),
    }


def main():
    print("restem eval_v2: hardcoded 440Hz basis vs. estimated-basis fix, across varied interferer frequencies")
    print(f"published (interferer=440.0Hz, matches the hardcoded basis exactly): {run_hardcoded_basis()}")
    print(f"same case, interferer=439.5Hz (0.5Hz off the hardcoded basis):        "
          f"{run_hardcoded_basis(interferer_freq=439.5)}")
    for label, seeds in (("tuning", TUNING_SEEDS), ("holdout", HOLDOUT_SEEDS)):
        print(f"\n{label} ({len(seeds)} seeds, varied interferer frequencies):")
        print(json.dumps(summarize(seeds), indent=2))


if __name__ == "__main__":
    main()
