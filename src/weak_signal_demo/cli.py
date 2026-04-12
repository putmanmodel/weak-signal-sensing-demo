from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from src.weak_signal_demo.baseline import FlatScoreBaseline
from src.weak_signal_demo.config import DemoConfig
from src.weak_signal_demo.deviation import DeviationEvaluationLayer
from src.weak_signal_demo.partials import SensorPartialsLayer
from src.weak_signal_demo.reflex import ReflexSalienceLayer
from src.weak_signal_demo.scenarios import SCENARIOS, get_scenario
from src.weak_signal_demo.signals import generate_observations
from src.weak_signal_demo.state_machine import CandidateStateMachine
from src.weak_signal_demo.types import CandidateState, RunSummary, StepRecord


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Weak-signal sensing architecture demo")
    parser.add_argument("--scenario", default="cross_channel_support", choices=sorted(SCENARIOS))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--no-plot", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = DemoConfig(seed=args.seed)
    scenario = get_scenario(args.scenario)
    output_dir = Path(args.output_dir)

    records, summary = run_scenario(scenario.name, config, quiet=args.quiet)

    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / f"{scenario.name}.json"
    summary_path = output_dir / f"{scenario.name}_summary.json"
    log_path.write_text(json.dumps([record.to_dict() for record in records], indent=2))
    summary_path.write_text(json.dumps(summary.to_dict(), indent=2))

    plot_path = None
    if not args.no_plot:
        os.environ.setdefault("MPLCONFIGDIR", str(output_dir / ".mplconfig"))
        from src.weak_signal_demo.plotting import save_run_plot

        plot_path = save_run_plot(records, scenario.name, output_dir)

    if not args.quiet:
        print()
        print("Summary")
        print(f"  Scenario: {scenario.name}")
        print(f"  Final layered state: {summary.final_state}")
        print(f"  Governed promotions at timesteps: {summary.promoted_steps or 'none'}")
        print(f"  Quarantines at timesteps: {summary.quarantined_steps or 'none'}")
        print(f"  Baseline detections at timesteps: {summary.baseline_detected_steps or 'none'}")
        print(f"  JSON log: {log_path}")
        print(f"  Summary report: {summary_path}")
        if plot_path is not None:
            print(f"  Plot: {plot_path}")

    return 0


def run_scenario(scenario_name: str, config: DemoConfig, quiet: bool = False) -> tuple[list[StepRecord], RunSummary]:
    scenario = get_scenario(scenario_name)
    observations = generate_observations(scenario, seed=config.seed)

    partials_layer = SensorPartialsLayer()
    reflex_layer = ReflexSalienceLayer(config)
    deviation_layer = DeviationEvaluationLayer(config)
    state_machine = CandidateStateMachine(config)
    baseline = FlatScoreBaseline()

    records: list[StepRecord] = []

    if not quiet:
        print(f"Scenario: {scenario.name}")
        print(scenario.description)
        print("-" * 88)

    for observation in observations:
        partials = partials_layer.update(observation)
        salience = reflex_layer.update(partials)
        deviation = deviation_layer.update(partials, salience)
        state, transition = state_machine.update(salience, deviation)
        baseline_output = baseline.update(partials)

        record = StepRecord(
            timestep=observation.timestep,
            observation=observation,
            partials=partials,
            salience=salience,
            deviation=deviation,
            state=state,
            transition=transition,
            baseline=baseline_output,
        )
        records.append(record)

        if not quiet:
            print(_format_log_line(record))
            if transition is not None:
                print(f"    transition: {transition.from_state.value} -> {transition.to_state.value} ({transition.reason})")

    summary = RunSummary(
        scenario=scenario.name,
        steps=len(records),
        final_state=records[-1].state.value if records else CandidateState.DECAYED.value,
        promoted_steps=[
            r.timestep for r in records if r.state is CandidateState.GOVERNED_CANDIDATE
        ],
        quarantined_steps=[
            r.timestep for r in records if r.state is CandidateState.QUARANTINED
        ],
        baseline_detected_steps=[
            r.timestep for r in records if r.baseline.detected
        ],
    )
    return records, summary


def _format_log_line(record: StepRecord) -> str:
    return (
        f"t={record.timestep:02d} "
        f"partials[a_per={record.partials.acoustic_periodicity:.2f}, "
        f"a_delta={record.partials.acoustic_snr_delta:.2f}, "
        f"m_persist={record.partials.motion_persistence:.2f}, "
        f"b_cons={record.partials.bearing_consistency:.2f}, "
        f"b_var={record.partials.bearing_variance:.2f}] "
        f"salience[a={record.salience.acoustic:.2f}, "
        f"m={record.salience.motion:.2f}, "
        f"b={record.salience.bearing:.2f}, total={record.salience.total:.2f}] "
        f"deviation[persist={record.deviation.persistence_windows}, "
        f"support={record.deviation.supporting_channels}, "
        f"b_var={record.deviation.bearing_variance:.2f}] "
        f"state={record.state.value} "
        f"baseline(score={record.baseline.score:.2f}, detected={record.baseline.detected})"
    )
