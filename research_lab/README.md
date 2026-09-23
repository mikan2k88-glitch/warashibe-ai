# Warashibe AI Research Lab

This directory is the control layer for experiments on the `research-lab` branch.

Principles:

- `main` is treated as the stable line.
- Experiments stay on `research-lab` until validated.
- The lab can recommend promotion but does not merge to `main` automatically.
- Research is evaluated against explicit metrics rather than version-number churn.
- Broad research stages may be declared mature when tests pass and repeated work has plateaued.

Initial tracks: route, recovery, speed, cost, real market, learning, integration.

Run the smoke test with:

    python -m research_lab.test_lab
