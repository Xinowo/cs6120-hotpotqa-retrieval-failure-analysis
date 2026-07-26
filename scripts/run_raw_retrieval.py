#!/usr/bin/env python
"""
run_raw_retrieval.py

Thin CLI entry point for the v2 raw retrieval runner. All logic lives in the
importable, offline-testable :mod:`src.raw_runner`; this wrapper only wires
``sys.argv`` to :func:`src.raw_runner.main` so the runner can also be launched as
a script (``python scripts/run_raw_retrieval.py --method dense --setting both``).

Transitional and additive: it publishes canonical v2 raw run bundles under
``results/retrieval_runs/<run-id>/`` and changes no existing runner or default.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.raw_runner import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
