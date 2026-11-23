import uuid
from dataclasses import dataclass

from opentelemetry import trace

from .judge import Judge, weighted_score
from .rubrics import Case, Criterion
from .store import ResultStore


@dataclass
class CaseResult:
    case_id: str
    output: str
    score: float


class Evaluator:
    """Runs a compiled LangGraph app over cases and scores each output with a judge."""

    def __init__(self, app, judge: Judge, rubric: list[Criterion], store: ResultStore | None = None,
                 input_key: str = "input", output_key: str = "output"):
        self.app, self.judge, self.rubric = app, judge, rubric
        self.store = store or ResultStore()
        self.input_key, self.output_key = input_key, output_key
        self.tracer = trace.get_tracer("agent_eval")

    def run(self, cases: list[Case]) -> list[CaseResult]:
        run_id = str(uuid.uuid4())
        results = []
        with self.tracer.start_as_current_span("eval.run") as run_span:
            run_span.set_attribute("eval.run_id", run_id)
            for case in cases:
                with self.tracer.start_as_current_span("eval.case") as span:
                    span.set_attribute("eval.case_id", case.id)
                    final = self.app.invoke({self.input_key: case.input})
                    output = str(final.get(self.output_key, ""))
                    with self.tracer.start_as_current_span("eval.judge"):
                        verdict = self.judge.evaluate(case, output, self.rubric)
                    score = weighted_score(verdict, self.rubric)
                    span.set_attribute("eval.score", score)
                    self.store.save(run_id, case.id, output, score, verdict.model_dump())
                    results.append(CaseResult(case.id, output, score))
        return results
