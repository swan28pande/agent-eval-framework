from pathlib import Path

import yaml
from pydantic import BaseModel


class Criterion(BaseModel):
    name: str
    description: str
    weight: float = 1.0


class Case(BaseModel):
    id: str
    input: str
    reference: str | None = None


def load_rubric(path: str | Path) -> list[Criterion]:
    data = yaml.safe_load(Path(path).read_text())
    return [Criterion(**r) for r in data["rubrics"]]


def load_cases(path: str | Path) -> list[Case]:
    data = yaml.safe_load(Path(path).read_text())
    return [Case(**c) for c in data["cases"]]
