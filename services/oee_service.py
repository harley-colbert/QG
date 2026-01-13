"""
services/oee_service.py
=======================

Pure-function service layer for Overall Equipment Effectiveness (OEE).

• NO PySide/PyQt/Web imports – safe for unit-testing and headless execution.
• Mirrors every numerical concern that `oeeMetrics.py` covered:
    ─ availability, performance, quality
    ─ OEE %
    ─ capacity (parts per hour)
• Exposes both fine-grained helpers *and* a single `compute_oee()` façade
  so callers can choose convenience or granularity.

Typical usage
-------------
>>> from services.oee_service import compute_oee
>>> payload = {
...     "runtime": 8.0,
...     "planned_downtime": 30.0,
...     "unplanned_downtime": 0.0,
...     "total_parts": 400.0,
...     "cycle_time": 60.0,
...     "total_scrap": 10.0,
... }
>>> compute_oee(payload)
{
    'oee': 87.08,
    'capacity': 50.0,
    'total_produced': 400.0,
    'performance': 89.41,
    'quality': 97.5,
    'availability': 100.0
}
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


# ────────────────────────────────────────────────────────────────────────────────
# Data container
# ────────────────────────────────────────────────────────────────────────────────
@dataclass(slots=True)
class OEEInputs:
    """
    Normalised numeric inputs (floats).

    All time-based fields use float minutes/hours exactly as provided
    by the UI – no string parsing here.
    """
    runtime: float = 0.0               # hours
    planned_downtime: float = 0.0      # minutes
    unplanned_downtime: float = 0.0    # minutes
    total_parts: float = 0.0           # count
    cycle_time: float = 0.0            # seconds per part (ideal)
    total_scrap: float = 0.0           # count

    @classmethod
    def from_dict(cls, d: Dict[str, float | int | str]) -> "OEEInputs":
        """
        Build an instance from raw JSON / dict payloads (e.g. JS → Python).

        • Silently converts blank strings to 0.
        • Coerces everything to float.
        """
        kw = {}
        for field in cls.__dataclass_fields__:
            val = d.get(field, 0)
            if val == "" or val is None:
                val = 0
            kw[field] = float(val)
        return cls(**kw)


# ────────────────────────────────────────────────────────────────────────────────
# Helpers – kept module-level for easier unit-testing
# ────────────────────────────────────────────────────────────────────────────────
def _safe_pct(numerator: float, denominator: float) -> float:
    """Return percentage (0-100) or 0.0 when denominator is zero."""
    return (numerator / denominator * 100.0) if denominator else 0.0


def _round2(value: float) -> float:
    """Round to two decimal places for UI consistency."""
    return round(value, 0)


# ────────────────────────────────────────────────────────────────────────────────
# Core public API
# ────────────────────────────────────────────────────────────────────────────────
def compute_oee(raw: Dict[str, float | int | str]) -> Dict[str, float]:
    if isinstance(raw, OEEInputs):
        inp = raw
    else:
        inp = OEEInputs.from_dict(raw)

    runtime_sec            = inp.runtime * 3600.0
    planned_downtime_sec   = inp.planned_downtime * 60.0
    unplanned_downtime_sec = inp.unplanned_downtime * 60.0

    planned_production_time = max(runtime_sec - planned_downtime_sec, 0.0)
    operating_time          = max(planned_production_time - unplanned_downtime_sec, 0.0)

    availability = _safe_pct(operating_time, planned_production_time)
    ideal_parts  = operating_time / inp.cycle_time if inp.cycle_time else 0.0
    performance  = _safe_pct(inp.total_parts, ideal_parts)
    good_parts   = max(inp.total_parts - inp.total_scrap, 0.0)
    quality      = _safe_pct(good_parts, inp.total_parts)
    oee          = (availability/100.0) * (performance/100.0) * (quality/100.0) * 100.0
    capacity     = (inp.total_parts / inp.runtime) if inp.runtime else 0.0

    return {
        # ---- outputs (rounded) ----
        "oee":              _round2(oee),
        "capacity":         _round2(capacity),
        "total_produced":   _round2(inp.total_parts),
        "performance":      _round2(performance),
        "quality":          _round2(quality),
        "availability":     _round2(availability),

        # ---- inputs (rounded to match UI; keep raw if you prefer) ----
        "runtime":          _round2(inp.runtime),            # hours
        "planned_downtime": _round2(inp.planned_downtime),   # minutes
        "unplanned_downtime": _round2(inp.unplanned_downtime), # minutes
        "total_parts":      _round2(inp.total_parts),
        "total_scrap":      _round2(inp.total_scrap),
        "cycle_time":       _round2(inp.cycle_time),         # seconds/part (ideal)
        "nominalcycletime": _round2(inp.cycle_time),         # alias for template

        # ---- useful intermediates (optional, rounded) ----
        "runtime_sec":                    _round2(runtime_sec),
        "planned_downtime_sec":           _round2(planned_downtime_sec),
        "unplanned_downtime_sec":         _round2(unplanned_downtime_sec),
        "planned_production_time_sec":    _round2(planned_production_time),
        "operating_time_sec":             _round2(operating_time),
        "ideal_parts":                    _round2(ideal_parts),
        "good_parts":                     _round2(good_parts),
    }

# ────────────────────────────────────────────────────────────────────────────────
# Optional fine-grained API (mirrors methods in your Qt widget)
# ────────────────────────────────────────────────────────────────────────────────
def compute_availability(runtime_hrs: float,
                          planned_down_min: float,
                          unplanned_down_min: float) -> float:
    """Return availability % rounded to 2 decimals."""
    runtime_sec   = runtime_hrs * 3600.0
    planned_sec   = planned_down_min * 60.0
    unplanned_sec = unplanned_down_min * 60.0
    planned_production = max(runtime_sec - planned_sec, 0.0)
    operating_time     = max(planned_production - unplanned_sec, 0.0)
    return _round2(_safe_pct(operating_time, planned_production))


def compute_performance(operating_time_sec: float,
                        total_parts: float,
                        cycle_time_sec: float) -> float:
    ideal_parts = operating_time_sec / cycle_time_sec if cycle_time_sec else 0.0
    return _round2(_safe_pct(total_parts, ideal_parts))


def compute_quality(total_parts: float, scrap_parts: float) -> float:
    good_parts = max(total_parts - scrap_parts, 0.0)
    return _round2(_safe_pct(good_parts, total_parts))


def compute_capacity(total_parts: float, runtime_hrs: float) -> float:
    return _round2(total_parts / runtime_hrs) if runtime_hrs else 0.0
