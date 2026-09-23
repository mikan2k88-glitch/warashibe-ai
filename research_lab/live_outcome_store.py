"""Local research-only store for observed sale outcomes.

The JSON file is intentionally simple and portable. It does not fabricate outcomes:
only explicitly supplied SaleOutcome records are persisted.
"""

import json
import os
from dataclasses import asdict
from pathlib import Path

from research_lab.raw_outcome_calibration import SaleOutcome

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = Path(os.environ.get("WARASHIBE_OUTCOME_STORE", ROOT / "research_output" / "sale_outcomes.json"))


class OutcomeStore:
    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []
        try:
            rows = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [
            SaleOutcome(
                opportunity_key=str(row["opportunity_key"]),
                sold=bool(row["sold"]),
                days_to_outcome=row.get("days_to_outcome"),
            )
            for row in rows
            if "opportunity_key" in row and "sold" in row
        ]

    def append(self, outcome):
        rows = self.load()
        rows.append(outcome)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([asdict(row) for row in rows], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return len(rows)

    def for_opportunity(self, opportunity_key):
        return [x for x in self.load() if x.opportunity_key == opportunity_key]

    def stats(self):
        rows = self.load()
        sold = sum(1 for x in rows if x.sold)
        return {
            "mode": "persisted_research" if rows else "waiting",
            "total": len(rows),
            "sold": sold,
            "failed": len(rows) - sold,
            "opportunities": len({x.opportunity_key for x in rows}),
        }
