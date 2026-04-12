from __future__ import annotations

from src.weak_signal_demo.types import ScenarioDefinition


SCENARIOS: dict[str, ScenarioDefinition] = {
    "clutter_only": ScenarioDefinition(
        name="clutter_only",
        steps=60,
        description="No coherent target, only noisy local clutter and random bearing wobble.",
        event_start=20,
        event_end=32,
        acoustic_gain=0.16,
        modulation_gain=0.10,
        motion_gain=0.18,
        bearing_lock_strength=0.05,
        brief_spike=False,
    ),
    "weak_anomaly_fades": ScenarioDefinition(
        name="weak_anomaly_fades",
        steps=60,
        description="A weak anomaly appears, looks interesting briefly, then dissolves before support builds.",
        event_start=18,
        event_end=38,
        acoustic_gain=0.28,
        modulation_gain=0.22,
        motion_gain=0.24,
        bearing_lock_strength=0.18,
        fade_after_peak=True,
    ),
    "weak_anomaly_persists": ScenarioDefinition(
        name="weak_anomaly_persists",
        steps=60,
        description="A weak anomaly persists long enough to accumulate evidence across time.",
        event_start=16,
        event_end=46,
        acoustic_gain=0.32,
        modulation_gain=0.30,
        motion_gain=0.30,
        bearing_lock_strength=0.28,
    ),
    "cross_channel_support": ScenarioDefinition(
        name="cross_channel_support",
        steps=60,
        description="Channels are individually weak but align over time, enabling governed promotion.",
        event_start=14,
        event_end=44,
        acoustic_gain=0.26,
        modulation_gain=0.34,
        motion_gain=0.28,
        bearing_lock_strength=0.32,
    ),
    "false_positive_brief": ScenarioDefinition(
        name="false_positive_brief",
        steps=60,
        description="A short, strong local anomaly excites the baseline detector but does not persist structurally.",
        event_start=24,
        event_end=29,
        acoustic_gain=0.42,
        modulation_gain=0.16,
        motion_gain=0.12,
        bearing_lock_strength=0.08,
        brief_spike=True,
    ),
    "distributed_nodes": ScenarioDefinition(
        name="distributed_nodes",
        steps=60,
        description="Two weak nodes contribute partial evidence that becomes more interpretable when combined centrally.",
        event_start=15,
        event_end=45,
        acoustic_gain=0.24,
        modulation_gain=0.26,
        motion_gain=0.24,
        bearing_lock_strength=0.30,
        node_count=2,
    ),
}


def get_scenario(name: str) -> ScenarioDefinition:
    if name not in SCENARIOS:
        valid = ", ".join(sorted(SCENARIOS))
        raise KeyError(f"Unknown scenario '{name}'. Valid scenarios: {valid}")
    return SCENARIOS[name]
