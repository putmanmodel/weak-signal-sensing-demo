from __future__ import annotations

from src.weak_signal_demo.types import BaselineOutput, ChannelPartials


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


class FlatScoreBaseline:
    """A deliberately simple flat detector for behavioral comparison."""

    def __init__(self, threshold: float = 0.33) -> None:
        self.threshold = threshold

    def update(self, partials: ChannelPartials) -> BaselineOutput:
        score = clamp(
            0.30 * partials.acoustic_periodicity
            + 0.20 * partials.acoustic_snr_delta
            + 0.25 * partials.motion_persistence
            + 0.25 * partials.bearing_consistency
        )
        return BaselineOutput(score=round(score, 4), detected=score >= self.threshold)
