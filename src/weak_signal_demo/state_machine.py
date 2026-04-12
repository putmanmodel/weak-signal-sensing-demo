from __future__ import annotations

from src.weak_signal_demo.config import DemoConfig
from src.weak_signal_demo.types import (
    CandidateState,
    DeviationAssessment,
    SalienceOutput,
    TransitionEvent,
)


class CandidateStateMachine:
    """Explicit deterministic state transitions for provisional evidence."""

    def __init__(self, config: DemoConfig) -> None:
        self.config = config
        self.state = CandidateState.DECAYED

    def update(
        self,
        salience: SalienceOutput,
        deviation: DeviationAssessment,
    ) -> tuple[CandidateState, TransitionEvent | None]:
        next_state = self._decide_state(salience, deviation)
        transition = None
        if next_state != self.state:
            transition = TransitionEvent(
                from_state=self.state,
                to_state=next_state,
                reason=self._reason_for(next_state, salience, deviation),
            )
            self.state = next_state
        return self.state, transition

    def _decide_state(
        self,
        salience: SalienceOutput,
        deviation: DeviationAssessment,
    ) -> CandidateState:
        if self._should_promote(deviation):
            return CandidateState.GOVERNED_CANDIDATE
        if self._should_quarantine(salience, deviation):
            return CandidateState.QUARANTINED
        if deviation.structurally_meaningful or salience.total >= self.config.interpreted_gate:
            return CandidateState.INTERPRETED_CANDIDATE
        if salience.total >= self.config.salience_gate:
            return CandidateState.SALIENT
        if salience.total >= self.config.decay_gate:
            return CandidateState.OBSERVED
        return CandidateState.DECAYED

    def _should_promote(self, deviation: DeviationAssessment) -> bool:
        return (
            deviation.persistence_windows >= self.config.promotion_persistence
            and deviation.supporting_channels >= self.config.promotion_supporting_channels
            and deviation.bearing_variance <= self.config.bearing_variance_threshold
        )

    def _should_quarantine(
        self,
        salience: SalienceOutput,
        deviation: DeviationAssessment,
    ) -> bool:
        local_peak = max(salience.acoustic, salience.motion, salience.bearing)
        return (
            (salience.total >= self.config.quarantine_salience_gate or local_peak >= 0.9)
            and deviation.supporting_channels < 2
            and deviation.persistence_windows <= 2
        )

    def _reason_for(
        self,
        next_state: CandidateState,
        salience: SalienceOutput,
        deviation: DeviationAssessment,
    ) -> str:
        if next_state is CandidateState.GOVERNED_CANDIDATE:
            return (
                "promotion rule passed: persistence >= "
                f"{self.config.promotion_persistence}, support >= "
                f"{self.config.promotion_supporting_channels}, bearing variance stable"
            )
        if next_state is CandidateState.QUARANTINED:
            return "high local salience without durable multi-channel support"
        if next_state is CandidateState.INTERPRETED_CANDIDATE:
            return "pattern is structurally meaningful but still provisional"
        if next_state is CandidateState.SALIENT:
            return f"transient salience above {self.config.salience_gate:.2f}"
        if next_state is CandidateState.OBSERVED:
            return "weak cues noticed without enough support for stronger interpretation"
        return f"evidence decayed below {self.config.decay_gate:.2f}"
