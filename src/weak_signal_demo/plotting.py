from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from src.weak_signal_demo.types import CandidateState, StepRecord


STATE_TO_NUMERIC = {
    CandidateState.DECAYED: 0,
    CandidateState.OBSERVED: 1,
    CandidateState.SALIENT: 2,
    CandidateState.INTERPRETED_CANDIDATE: 3,
    CandidateState.QUARANTINED: 4,
    CandidateState.GOVERNED_CANDIDATE: 5,
}


def save_run_plot(records: list[StepRecord], scenario: str, output_dir: Path) -> Path:
    timesteps = [record.timestep for record in records]

    fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)

    axes[0].plot(timesteps, [r.observation.acoustic_level for r in records], label="acoustic level")
    axes[0].plot(timesteps, [r.observation.motion_level for r in records], label="motion level")
    axes[0].plot(timesteps, [r.observation.bearing_quality for r in records], label="bearing quality")
    axes[0].set_ylabel("signal")
    axes[0].set_title(f"Weak-signal sensing demo: {scenario}")
    axes[0].legend(loc="upper right")

    axes[1].plot(timesteps, [r.salience.acoustic for r in records], label="acoustic salience")
    axes[1].plot(timesteps, [r.salience.motion for r in records], label="motion salience")
    axes[1].plot(timesteps, [r.salience.bearing for r in records], label="bearing salience")
    axes[1].plot(timesteps, [r.salience.total for r in records], label="total salience", linewidth=2.2)
    axes[1].set_ylabel("salience")
    axes[1].legend(loc="upper right")

    axes[2].step(
        timesteps,
        [STATE_TO_NUMERIC[r.state] for r in records],
        where="mid",
        label="layered state",
    )
    axes[2].set_ylabel("state")
    axes[2].set_yticks(list(STATE_TO_NUMERIC.values()), [state.value for state in STATE_TO_NUMERIC])
    axes[2].legend(loc="upper right")

    axes[3].plot(timesteps, [r.baseline.score for r in records], label="baseline score")
    axes[3].step(
        timesteps,
        [1.0 if r.baseline.detected else 0.0 for r in records],
        where="mid",
        label="baseline detected",
    )
    axes[3].set_ylabel("baseline")
    axes[3].set_xlabel("timestep")
    axes[3].legend(loc="upper right")

    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{scenario}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
