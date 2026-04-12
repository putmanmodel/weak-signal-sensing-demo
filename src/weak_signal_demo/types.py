from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class CandidateState(str, Enum):
    OBSERVED = "observed"
    SALIENT = "salient"
    INTERPRETED_CANDIDATE = "interpreted_candidate"
    GOVERNED_CANDIDATE = "governed_candidate"
    DECAYED = "decayed"
    QUARANTINED = "quarantined"


@dataclass(frozen=True)
class RawObservation:
    timestep: int
    acoustic_level: float
    acoustic_modulation: float
    motion_level: float
    motion_jitter: float
    bearing_angle: float
    bearing_quality: float
    node_count: int = 1


@dataclass(frozen=True)
class ChannelPartials:
    acoustic_periodicity: float
    acoustic_snr_delta: float
    motion_persistence: float
    bearing_consistency: float
    bearing_variance: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class SalienceOutput:
    acoustic: float
    motion: float
    bearing: float
    total: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class DeviationAssessment:
    persistence_windows: int
    supporting_channels: int
    bearing_variance: float
    salience_hit_count: int
    structurally_meaningful: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionEvent:
    from_state: CandidateState
    to_state: CandidateState
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class BaselineOutput:
    score: float
    detected: bool

    def as_dict(self) -> dict[str, float | bool]:
        return asdict(self)


@dataclass
class StepRecord:
    timestep: int
    observation: RawObservation
    partials: ChannelPartials
    salience: SalienceOutput
    deviation: DeviationAssessment
    state: CandidateState
    transition: TransitionEvent | None
    baseline: BaselineOutput

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "timestep": self.timestep,
            "observation": asdict(self.observation),
            "partials": self.partials.as_dict(),
            "salience": self.salience.as_dict(),
            "deviation": self.deviation.as_dict(),
            "state": self.state.value,
            "baseline": self.baseline.as_dict(),
        }
        if self.transition is not None:
            payload["transition"] = self.transition.as_dict()
        return payload


@dataclass(frozen=True)
class ScenarioDefinition:
    name: str
    steps: int
    description: str
    event_start: int
    event_end: int
    acoustic_gain: float
    modulation_gain: float
    motion_gain: float
    bearing_lock_strength: float
    node_count: int = 1
    fade_after_peak: bool = False
    brief_spike: bool = False


@dataclass
class RunSummary:
    scenario: str
    steps: int
    final_state: str
    promoted_steps: list[int] = field(default_factory=list)
    quarantined_steps: list[int] = field(default_factory=list)
    baseline_detected_steps: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
