"""Separate hypothetical storage; never feeds observed commerce outcomes.

JSON persistence is for a single-process local research deployment. A future
Supabase adapter must enforce the same protocol with RLS and atomic writes.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from typing import Protocol


class ShadowRepository(Protocol):
    def add(self, candidate: dict) -> None: ...
    def get(self, shadow_candidate_id: str) -> dict: ...
    def load(self) -> list[dict]: ...
    def observe(self, shadow_candidate_id: str, observation: dict) -> None: ...
    def observations(self, shadow_candidate_id: str) -> list[dict]: ...
    def finish(self, shadow_candidate_id: str, outcome: dict) -> None: ...


def _safe(record):
    if not isinstance(record, dict):
        raise ValueError("shadow record must be a mapping")
    if (record.get("external_execution_authorized") is not False
            or record.get("purchase_authorized") is not False
            or record.get("human_gate_required") is not True):
        raise ValueError("shadow safety boundary missing")
    for key, value in record.items():
        if key.endswith("authorized") and value is not False:
            raise ValueError("shadow cannot carry execution authority")


class InMemoryShadowRepository:
    def __init__(self):
        self._candidates, self._observations, self._outcomes = {}, {}, {}

    def add(self, candidate):
        _safe(candidate)
        key = candidate.get("shadow_candidate_id")
        if (not isinstance(key, str) or not key.strip() or key in self._candidates
                or candidate.get("maturity_stage") != "shadow" or candidate.get("status") != "active"):
            raise ValueError("invalid or duplicate shadow candidate")
        self._candidates[key] = deepcopy(candidate)
        self._observations[key] = []

    def get(self, key):
        row = deepcopy(self._candidates[key])
        if key in self._outcomes:
            row["outcome"] = deepcopy(self._outcomes[key])
            row["status"] = "invalidated" if row["outcome"]["outcome_status"] == "invalidated" else "completed"
        return row

    def load(self):
        return [self.get(key) for key in self._candidates]

    def observe(self, key, observation):
        self.get(key)
        _safe(observation)
        if key in self._outcomes or observation.get("shadow_candidate_id") != key:
            raise ValueError("shadow closed or observation mismatched")
        self._observations[key].append(deepcopy(observation))

    def observations(self, key):
        self.get(key)
        return deepcopy(self._observations[key])

    def finish(self, key, outcome):
        self.get(key)
        _safe(outcome)
        if key in self._outcomes or outcome.get("shadow_candidate_id") != key:
            raise ValueError("shadow closed or outcome mismatched")
        if outcome.get("outcome_status") not in {"success", "loss", "unsold", "invalidated", "insufficient_evidence"}:
            raise ValueError("invalid shadow outcome")
        self._outcomes[key] = deepcopy(outcome)


class JsonShadowRepository(InMemoryShadowRepository):
    """Explicit opt-in local evidence writes; corruption is an error, never empty data."""
    def __init__(self, path):
        super().__init__()
        self.path = Path(path)
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if data.get("version") != 1:
                raise ValueError("unsupported shadow repository version")
            for candidate in data["candidates"]:
                super().add(candidate)
            for key, rows in data["observations"].items():
                for row in rows:
                    super().observe(key, row)
            for key, row in data["outcomes"].items():
                super().finish(key, row)

    def _mutate(self, method, *args):
        before = deepcopy((self._candidates, self._observations, self._outcomes))
        temp = None
        try:
            method(*args)
            payload = json.dumps({"version": 1, "candidates": list(self._candidates.values()),
                                  "observations": self._observations, "outcomes": self._outcomes},
                                 ensure_ascii=False, allow_nan=False, indent=2)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             delete=False, suffix=".tmp") as stream:
                temp = stream.name
                stream.write(payload)
            os.replace(temp, self.path)
        except Exception:
            self._candidates, self._observations, self._outcomes = before
            raise
        finally:
            if temp and os.path.exists(temp):
                os.unlink(temp)

    def add(self, candidate):
        self._mutate(super().add, candidate)

    def observe(self, key, observation):
        self._mutate(super().observe, key, observation)

    def finish(self, key, outcome):
        self._mutate(super().finish, key, outcome)
