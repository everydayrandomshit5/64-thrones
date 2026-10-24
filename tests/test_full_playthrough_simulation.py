"""
test_full_playthrough_simulation.py - Automated End-to-End Campaign Playthrough & QA Tests.
Part of Verification for 64-Thrones: High-Glamour Edition (v3.2).
"""

import pytest
from pathlib import Path
from tools.verify_all_scripts import check_script_integrity
from tools.simulate_full_campaign import run_full_simulation

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_renpy_script_linter_zero_errors():
    """Verify static analysis of all .rpy scripts passes with zero missing assets or broken labels."""
    try:
        check_script_integrity()
    except SystemExit as e:
        assert e.code == 0, "Script integrity check failed with errors"


def test_full_17_chapter_campaign_simulation():
    """Simulates live match sessions for all 17 chapters, spells, advisors, camp hub, and 8 endings."""
    try:
        run_full_simulation()
    except SystemExit as e:
        assert e.code == 0, "Full campaign simulation failed with errors"
