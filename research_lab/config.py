"""Configuration for the autonomous research loop."""

LAB_BRANCH = "research-lab"
PRODUCTION_BRANCH = "main"
TARGET_CAPITAL = 1_000_000
START_CAPITAL = 100

# A research result must be reproducible before it becomes a promotion candidate.
MIN_REPEATS = 3

# Promotion remains human-approved. The lab may recommend, never merge by itself.
REQUIRE_HUMAN_APPROVAL = True

RESEARCH_TRACKS = [
    "route",
    "recovery",
    "speed",
    "cost",
    "real_market",
    "learning",
    "integration",
]
