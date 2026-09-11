#!/usr/bin/env python3
"""Fail-closed trainable-surface census for Signal-Prophet.

Signal-Prophet currently implements deterministic/symbolic signals-and-systems
analysis rather than learned model fitting.  This authority prevents that fact from
becoming a silent exemption: any future ML framework, estimator fit, gradient
optimizer or neural-training primitive blocks the central controller until wired.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ML_ROOTS = {
    "torch", "tensorflow", "keras", "sklearn", "jax", "flax", "optax",
    "xgboost", "lightgbm", "catboost", "transformers", "stable_baselines3",
}
TRAIN_CALLS = {"fit", "partial_fit", "backward", "minimize", "train_step", "optimizer_step"}


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    kind: str
    symbol: str


def audit() -> dict[str, object]:
    findings: list[Finding] = []
    scanned: list[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(("api/tests/", "training_control/", ".training_control/")):
            continue
        scanned.append(relative)
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in ML_ROOTS:
                        findings.append(Finding(relative, node.lineno, "ml_import", alias.name))
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                if root in ML_ROOTS:
                    findings.append(Finding(relative, node.lineno, "ml_import", node.module))
            elif isinstance(node, ast.Call):
                target = node.func
                symbol = target.attr if isinstance(target, ast.Attribute) else target.id if isinstance(target, ast.Name) else ""
                if symbol in TRAIN_CALLS:
                    findings.append(Finding(relative, node.lineno, "training_call", symbol))
    if not scanned:
        raise RuntimeError("Signal-Prophet source census found no retained Python code")
    return {
        "schema_version": 1,
        "repository": "Anurag9000/Signal-Prophet",
        "classification": "deterministic_symbolic_signal_analysis" if not findings else "trainable_surface_detected",
        "scanned_files": scanned,
        "findings": [asdict(row) for row in findings],
        "no_trainable_surface": not findings,
        "scientific_modules": [
            "api/core/fourier.py",
            "api/core/period_detection.py",
            "api/core/roc_3d.py",
            "api/core/symbolic.py",
            "api/core/system_analyzer.py",
        ],
        "source_configuration_only": True,
        "execution_claim_emitted": False,
        "training_claim_emitted": False,
    }
