"""LLM-as-judge scoring against a configurable rubric."""

import os
from typing import Protocol

import anthropic
from pydantic import BaseModel, Field

from .rubrics import Case, Criterion


class CriterionScore(BaseModel):
    criterion: str
    score: int = Field(description="1 (poor) to 5 (excellent)")
    reasoning: str


class Verdict(BaseModel):
    scores: list[CriterionScore]


class Judge(Protocol):
    def evaluate(self, case: Case, output: str, rubric: list[Criterion]) -> Verdict: ...


class ClaudeJudge:
    def __init__(self, model: str | None = None):
        self.client = anthropic.Anthropic()
        self.model = model or os.getenv("JUDGE_MODEL", "claude-opus-5-5")

    def evaluate(self, case: Case, output: str, rubric: list[Criterion]) -> Verdict:
        criteria = "\n".join(f"- {c.name}: {c.description}" for c in rubric)
        prompt = (
            "You are grading the output of a multi-agent workflow.\n\n"
            f"Task:\n{case.input}\n\n"
            f"Reference answer (may be empty):\n{case.reference or ''}\n\n"
            f"Workflow output:\n{output}\n\n"
            f"Score each criterion from 1 to 5 with brief reasoning:\n{criteria}"
        )
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}],
            output_format=Verdict,
        )
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise RuntimeError(f"Judge returned no verdict (stop_reason={response.stop_reason})")
        return response.parsed_output


class ExactMatchJudge:
    """Offline judge for smoke tests: full marks if the reference appears in the output."""

    def evaluate(self, case: Case, output: str, rubric: list[Criterion]) -> Verdict:
        hit = bool(case.reference) and case.reference.lower() in output.lower()
        return Verdict(
            scores=[
                CriterionScore(criterion=c.name, score=5 if hit else 1, reasoning="exact match" if hit else "no match")
                for c in rubric
            ]
        )


def weighted_score(verdict: Verdict, rubric: list[Criterion]) -> float:
    weights = {c.name: c.weight for c in rubric}
    total = sum(weights.values()) or 1.0
    return sum(s.score * weights.get(s.criterion, 0.0) for s in verdict.scores) / total
