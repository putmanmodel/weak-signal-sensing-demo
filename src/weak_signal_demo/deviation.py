from __future__ import annotations

from collections import deque

import numpy as np

from src.weak_signal_demo.config import DemoConfig
from src.weak_signal_demo.types import ChannelPartials, DeviationAssessment, SalienceOutput


class DeviationEvaluationLayer:
    """Accumulates evidence across windows to see whether structure is emerging."""

    def __init__(self, config: DemoConfig) -> None:
        self.config = config
        self._salience_history: deque[SalienceOutput] = deque(maxlen=config.deviation_window)
        self._partials_history: deque[ChannelPartials] = deque(maxlen=config.deviation_window)

    def update(
        self,
        partials: ChannelPartials,
        salience: SalienceOutput,
    ) -> DeviationAssessment:
        self._partials_history.append(partials)
        self._salience_history.append(salience)

        salience_history = list(self._salience_history)
        persistence_windows = sum(
            1 for item in salience_history if item.total >= self.config.salience_gate
        )
        supporting_channels = sum(
            1
            for channel in ("acoustic", "motion", "bearing")
            if float(np.mean([getattr(item, channel) for item in salience_history]))
            >= self.config.channel_support_gate
        )
        mean_bearing_variance = float(
            np.mean([item.bearing_variance for item in self._partials_history])
        )
        salience_hit_count = sum(
            1
            for item in salience_history
            for channel in ("acoustic", "motion", "bearing")
            if getattr(item, channel) >= self.config.channel_support_gate
        )

        structurally_meaningful = (
            persistence_windows >= 2
            and supporting_channels >= 2
            and mean_bearing_variance <= self.config.bearing_variance_threshold * 1.35
        )

        return DeviationAssessment(
            persistence_windows=persistence_windows,
            supporting_channels=supporting_channels,
            bearing_variance=round(mean_bearing_variance, 4),
            salience_hit_count=salience_hit_count,
            structurally_meaningful=structurally_meaningful,
        )
