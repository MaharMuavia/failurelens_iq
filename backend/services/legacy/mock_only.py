from __future__ import annotations

"""
Legacy mock-only helpers.

Production API routes should not import this module. It exists only as a
quarantine area for old deterministic demos and documentation examples.
"""

from typing import Any


def build_legacy_mock_notice(exp: Any) -> dict[str, Any]:
    return {
        "mode": "offline_mock_preview",
        "is_live_backend": False,
        "is_live_microsoft_iq": False,
        "proof_level": "offline_mock_preview",
        "warning": "Legacy offline mock preview only. Do not use as live submission proof.",
        "experiment_id": getattr(exp, "experiment_id", ""),
    }
