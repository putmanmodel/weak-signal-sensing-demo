from __future__ import annotations

from collections import deque

import numpy as np

from src.weak_signal_demo.types import ChannelPartials, RawObservation


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


class SensorPartialsLayer:
    """Computes bounded local findings without making a global claim."""

    def __init__(self, history_size: int = 6) -> None:
        self._motion_history: deque[float] = deque(maxlen=history_size)
        self._bearing_history: deque[float] = deque(maxlen=history_size)
        self._acoustic_history: deque[float] = deque(maxlen=history_size)

    def update(self, observation: RawObservation) -> ChannelPartials:
        self._motion_history.append(observation.motion_level)
        self._bearing_history.append(observation.bearing_angle)
        self._acoustic_history.append(observation.acoustic_level)

        motion_mean = float(np.mean(self._motion_history))
        motion_persistence = clamp(
            0.55 * observation.motion_level + 0.45 * motion_mean - 0.35 * observation.motion_jitter
        )

        acoustic_mean = float(np.mean(self._acoustic_history))
        acoustic_periodicity = clamp(
            0.65 * observation.acoustic_modulation + 0.35 * observation.acoustic_level
        )
        acoustic_snr_delta = clamp(0.5 + (observation.acoustic_level - acoustic_mean) * 1.7)

        if len(self._bearing_history) >= 3:
            variance = float(np.var(self._bearing_history)) / 400.0
        else:
            variance = 0.35
        bearing_consistency = clamp(
            observation.bearing_quality * (1.0 - clamp(variance, 0.0, 0.95))
        )
        bearing_variance = clamp(variance)

        return ChannelPartials(
            acoustic_periodicity=round(acoustic_periodicity, 4),
            acoustic_snr_delta=round(acoustic_snr_delta, 4),
            motion_persistence=round(motion_persistence, 4),
            bearing_consistency=round(bearing_consistency, 4),
            bearing_variance=round(bearing_variance, 4),
        )
