from __future__ import annotations

from collections import deque

import numpy as np

from src.weak_signal_demo.config import DemoConfig
from src.weak_signal_demo.types import ChannelPartials, SalienceOutput


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


class ReflexSalienceLayer:
    """Short-horizon micro-baseline comparison without durable state."""

    def __init__(self, config: DemoConfig) -> None:
        self.config = config
        self._history: deque[dict[str, float]] = deque(maxlen=config.baseline_window)

    def update(self, partials: ChannelPartials) -> SalienceOutput:
        current = {
            "acoustic": 0.6 * partials.acoustic_periodicity + 0.4 * partials.acoustic_snr_delta,
            "motion": partials.motion_persistence,
            "bearing": 0.7 * partials.bearing_consistency + 0.3 * (1.0 - partials.bearing_variance),
        }
        salience = {
            key: self._score_against_baseline(key, value)
            for key, value in current.items()
        }
        self._history.append(current)
        total = round(float(np.mean(list(salience.values()))), 4)
        return SalienceOutput(
            acoustic=round(salience["acoustic"], 4),
            motion=round(salience["motion"], 4),
            bearing=round(salience["bearing"], 4),
            total=total,
        )

    def _score_against_baseline(self, key: str, value: float) -> float:
        if len(self._history) < 3:
            return clamp(max(0.0, value - 0.35) * 1.4)
        baseline = np.array([item[key] for item in self._history], dtype=float)
        mean = float(np.mean(baseline))
        std = float(np.std(baseline))
        delta = max(0.0, value - mean - 0.03)
        normalized = delta / (std + 0.12)
        return clamp(normalized)
