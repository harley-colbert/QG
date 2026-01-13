# services/pmcalc.py
"""
ProjectMilestonesCalculator
───────────────────────────
Reads lead-time data from an .xlsb, converts dates to week offsets,
and calculates standard project milestones.

* Fixes internal-row alignment:
    raw_data_2d: [stage:str, start_serial:float, end_serial:float]
* Uses zero-based indices consistently after the read.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Any, List

import pyxlsb  # pip install pyxlsb

# ────────────────────────────────────────────────────────────────────────────────
# Constants – make the mapping obvious.
# Excel rows/cols are 1-based; Python lists are 0-based.
# ────────────────────────────────────────────────────────────────────────────────
ROW_FIRST_STAGE = 9   # Excel row 10  → zero-based 9
COL_STAGE       = 1   # Excel col B   → zero-based 1
COL_START       = 5   # Excel col F   → zero-based 5
COL_END         = 6   # Excel col G   → zero-based 6

logger = logging.getLogger(__name__)


@dataclass
class MilestoneResults:
    customer_kickoff: int = 0
    design_acceptance: int = 0
    build_start: int = 0
    commissioning_start: int = 0
    fat_start: int = 0
    delivery: int = 0


class ProjectMilestonesCalculator:
    """
    Reads *Leadtime* sheet, converts dates to weeks, and derives milestones.
    """
    # ────────────────────────────────────────────────────────────────────
    # Construction
    # ────────────────────────────────────────────────────────────────────
    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.raw_data_2d: List[List[float]] = []   # [[stage, start_serial, end_serial], ...]
        self.with_extra_col: List[int] = []        # weeks per stage row
        self.final_values: MilestoneResults = MilestoneResults()

    # ────────────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────────────
    @staticmethod
    def _as_day_number(value: Any) -> int:
        """
        Normalise whatever we get from Excel into an *integer day count*
        so that simple subtraction == “days between”.
        """
        if value in (None, ""):
            raise ValueError("Empty cell")

        if isinstance(value, (int, float)):
            return int(value)

        if isinstance(value, (datetime, date)):
            return value.toordinal()

        raise TypeError(f"Unsupported cell type {type(value)} for {value!r}")

    # ────────────────────────────────────────────────────────────────────
    # Step 1 – Read Lead-time grid
    # ────────────────────────────────────────────────────────────────────
    def read_cost_grid_data(self) -> None:
        """
        Populate *self.raw_data_2d* with triples from **Leadtime!B10,F10,G10–B28,F28,G28**:

            [
              [stage:str, start_serial:float, end_serial:float],
              ...
            ]
        """
        ROW_LAST_STAGE = ROW_FIRST_STAGE + 18  # Excel row 28 → zero-based 27
        data: List[List[float]] = []

        try:
            with pyxlsb.open_workbook(self.filename) as wb:
                with wb.get_sheet("Leadtime") as sheet:
                    for r_idx, row in enumerate(sheet.rows()):
                        if r_idx < ROW_FIRST_STAGE or r_idx > ROW_LAST_STAGE:
                            continue

                        if len(row) <= COL_END:
                            logger.warning("PMCalc: row %d too short – skipped", r_idx + 1)
                            continue

                        stage_cell = row[COL_STAGE].v
                        start_cell = row[COL_START].v
                        end_cell   = row[COL_END].v

                        try:
                            start_serial = float(start_cell) if start_cell is not None else None
                            end_serial   = float(end_cell)   if end_cell   is not None else None
                        except (ValueError, TypeError):
                            logger.warning("PMCalc: non-numeric date(s) in row %d – skipped", r_idx + 1)
                            continue

                        if start_serial is None or end_serial is None:
                            logger.warning("PMCalc: blank date in row %d – skipped", r_idx + 1)
                            continue

                        stage = str(stage_cell).strip() if stage_cell is not None else f"Row{r_idx+1}"
                        data.append([stage, start_serial, end_serial])

        except Exception:
            logger.exception("PMCalc: error reading Leadtime!B10,G28")
            raise

        if not data:
            raise RuntimeError("PMCalc: no valid dates found in Leadtime!B10,G28")

        self.raw_data_2d = data
        logger.info("PMCalc: read %d rows from Leadtime!B10,G28", len(data))
        logger.debug("PMCalc: raw_data_2d = %s", self.raw_data_2d)

    # ────────────────────────────────────────────────────────────────────
    # Step 2 – Compute “D” (weeks-to-finish) column
    # ────────────────────────────────────────────────────────────────────
    def compute_d_column(self) -> None:
        """
        Builds *self.with_extra_col* – weeks from project start to each row’s end date.
        Logs every intermediate step.
        """
        # Ensure we have the data
        if not self.raw_data_2d:
            logger.info("PMCalc: raw_data empty – loading Leadtime data")
            self.read_cost_grid_data()

        # Project start = Leadtime!F10 (first data row’s *start* date)
        try:
            project_start_serial = self._as_day_number(self.raw_data_2d[0][1])
        except Exception as exc:
            raise RuntimeError("PMCalc: could not determine project start date (Leadtime!F10)") from exc

        logger.info("PMCalc: project_start serial = %s", project_start_serial)

        # Walk the stage rows
        self.with_extra_col = []
        for idx, row in enumerate(self.raw_data_2d):
            excel_row_num = ROW_FIRST_STAGE + idx + 1  # +1 to get Excel’s 1-based row
            try:
                stage        = row[0].strip() if isinstance(row[0], str) else str(row[0])
                start_serial = self._as_day_number(row[1])
                end_serial   = self._as_day_number(row[2])
            except Exception as exc:
                logger.error("PMCalc:   ! row %-2d %r  → %s", excel_row_num, row, exc)
                self.with_extra_col.append(0)
                continue

            numerator_days = end_serial - project_start_serial
            weeks_float    = numerator_days / 7
            weeks          = math.ceil(weeks_float) if numerator_days > 0 else 0
            self.with_extra_col.append(weeks)

            logger.debug(
                "PMCalc: Row %-2d | %-25s | start=%6d | end=%6d | "
                "num_days=%5d | weeks_flt=%8.3f | weeks=%2d",
                excel_row_num, stage, start_serial, end_serial,
                numerator_days, weeks_float, weeks
            )

        logger.info("PMCalc: final weeks column = %s", self.with_extra_col)

    # ────────────────────────────────────────────────────────────────────
    # Step 3 – Milestone formulas
    # ────────────────────────────────────────────────────────────────────
    def compute_final_values(self) -> None:
        """
        Applies milestone-specific formulas using *self.with_extra_col*:

            customer_kickoff    = 1
            design_acceptance   = max(D2, D3) + D4 – 1
            build_start         = D10 – 1
            commissioning_start = D12 – 1
            fat_start           = D15
            delivery            = D18
        """
        if not self.with_extra_col:
            logger.error("PMCalc: weeks data empty; run compute_d_column() first")
            raise ValueError("Weeks not computed before final values")

        d = self.with_extra_col
        if len(d) < 18:
            logger.error("PMCalc: insufficient rows (%d) for milestone formulas", len(d))
            raise ValueError("Insufficient rows in Leadtime data for milestone formulas")

        self.final_values.customer_kickoff       = 1
        self.final_values.design_acceptance      = max(d[1], d[2]) + d[3] - 1
        self.final_values.build_start            = d[9]  - 1  # row 10 - 1 => index 9
        self.final_values.commissioning_start    = d[11] - 1  # row 12 - 1 => index 11
        self.final_values.fat_start              = d[14]      # row 15 => index 14
        self.final_values.delivery               = d[17]      # row 18 => index 17

        logger.info("PMCalc: final milestone results: %s", self.final_values)

    # ────────────────────────────────────────────────────────────────────
    # Misc helpers (unchanged)
    # ────────────────────────────────────────────────────────────────────
    def get_project_cost(self) -> float:
        """
        Reads cell J306 from 'Summary' sheet and returns it as float.
        """
        try:
            with pyxlsb.open_workbook(self.filename) as wb:
                with wb.get_sheet("Summary") as sheet:
                    for idx, row in enumerate(sheet.rows(), start=1):
                        if idx == 306:
                            if len(row) >= 10 and row[9].v is not None:
                                try:
                                    return float(row[9].v)
                                except Exception:
                                    raise ValueError(f"Invalid cost value in J306: {row[9].v}")
                            raise ValueError("Cannot read cell J306 (row too short or empty)")
            raise ValueError("Sheet 'Summary' or row 306 not found")
        except Exception:
            logger.error("Error reading 'Summary' cost", exc_info=True)
            raise

    # ────────────────────────────────────────────────────────────────────
    # Convenience wrapper
    # ────────────────────────────────────────────────────────────────────
    def calculate_all(self) -> MilestoneResults:
        """
        read → compute weeks → derive milestones → return MilestoneResults
        """
        self.read_cost_grid_data()
        self.compute_d_column()
        self.compute_final_values()
        return self.final_values
