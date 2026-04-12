from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoConfig:
    seed: int = 7
    baseline_window: int = 6
    deviation_window: int = 5
    salience_gate: float = 0.32
    channel_support_gate: float = 0.28
    interpreted_gate: float = 0.5
    decay_gate: float = 0.14
    quarantine_salience_gate: float = 0.55
    bearing_variance_threshold: float = 0.12
    promotion_persistence: int = 3
    promotion_supporting_channels: int = 2
    log_every_step: bool = True
