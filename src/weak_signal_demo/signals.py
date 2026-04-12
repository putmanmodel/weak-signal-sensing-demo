from __future__ import annotations

import math

import numpy as np

from src.weak_signal_demo.types import RawObservation, ScenarioDefinition


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def generate_observations(
    scenario: ScenarioDefinition,
    seed: int,
) -> list[RawObservation]:
    rng = np.random.default_rng(seed)
    observations: list[RawObservation] = []
    stable_bearing = 35.0 + rng.normal(0.0, 2.0)

    for t in range(scenario.steps):
        event_strength = _event_strength(scenario, t)
        clutter_wave = 0.08 * math.sin(t / 4.8) + 0.05 * math.cos(t / 7.1)

        acoustic_level = clamp(
            0.36
            + clutter_wave
            + rng.normal(0.0, 0.06)
            + scenario.acoustic_gain * event_strength
            + 0.05 * (scenario.node_count - 1) * event_strength
        )
        acoustic_modulation = clamp(
            0.26
            + 0.04 * math.sin(t / 2.7)
            + rng.normal(0.0, 0.05)
            + scenario.modulation_gain * event_strength
        )

        motion_level = clamp(
            0.31
            + 0.05 * math.cos(t / 3.4)
            + rng.normal(0.0, 0.06)
            + scenario.motion_gain * event_strength
        )
        motion_jitter = clamp(
            0.42
            + rng.normal(0.0, 0.05)
            - 0.18 * scenario.motion_gain * event_strength
        )

        bearing_noise = max(1.5, 16.0 - 11.0 * scenario.bearing_lock_strength * event_strength)
        bearing_angle = (
            stable_bearing + rng.normal(0.0, bearing_noise)
            if event_strength > 0.02
            else rng.uniform(-90.0, 90.0)
        )
        bearing_quality = clamp(
            0.30
            + rng.normal(0.0, 0.05)
            + scenario.bearing_lock_strength * event_strength
            + 0.08 * (scenario.node_count - 1) * event_strength
        )

        observations.append(
            RawObservation(
                timestep=t,
                acoustic_level=round(acoustic_level, 4),
                acoustic_modulation=round(acoustic_modulation, 4),
                motion_level=round(motion_level, 4),
                motion_jitter=round(motion_jitter, 4),
                bearing_angle=round(bearing_angle, 4),
                bearing_quality=round(bearing_quality, 4),
                node_count=scenario.node_count,
            )
        )
    return observations


def _event_strength(scenario: ScenarioDefinition, timestep: int) -> float:
    if timestep < scenario.event_start or timestep > scenario.event_end:
        return 0.0

    span = max(1, scenario.event_end - scenario.event_start)
    position = (timestep - scenario.event_start) / span
    rise = min(1.0, position * 2.0)
    shape = 0.55 + 0.45 * math.sin(math.pi * position)

    if scenario.fade_after_peak:
        fade = max(0.1, 1.0 - position * 1.2)
        return clamp(shape * fade)

    if scenario.brief_spike:
        center = (scenario.event_start + scenario.event_end) / 2
        distance = abs(timestep - center)
        return clamp(1.0 - distance / 2.8)

    return clamp(max(rise, shape))
