"""The review host declaration: where a host keeps review reports and its baseline."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from acf.adr.contract import PosixStr
from acf.loader import load_model_file, require_file
from acf.repo import REVIEW_REL


class ReviewHostConfig(BaseModel):
    """The host values a review cannot derive."""

    model_config = ConfigDict(extra="forbid")

    report_dir: PosixStr = Field(min_length=1)
    baseline_path: PosixStr = Field(min_length=1)
    baseline_max_age_days: int = Field(gt=0)
    baseline_max_commits: int = Field(gt=0)
    packs: list[str]
    subsystems: list[PosixStr]
    exclude: list[str]


def load_review_config(repo: Path) -> ReviewHostConfig:
    """Load the host's review declaration; an absent file points at /acf-setup."""
    require_file(
        repo / REVIEW_REL, subject="review host config (run /acf-setup to create it)"
    )
    return load_model_file(
        repo / REVIEW_REL, ReviewHostConfig, subject="review host config", fmt="yaml"
    )
