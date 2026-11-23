import argparse

from .judge import ClaudeJudge, ExactMatchJudge
from .rubrics import load_cases, load_rubric
from .runner import Evaluator
from .sample_workflow import build_sample_workflow
from .tracing import setup_tracing


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate a LangGraph workflow")
    p.add_argument("--cases", default="examples/cases.yaml")
    p.add_argument("--rubric", default="rubrics.yaml")
    p.add_argument("--judge", choices=["claude", "exact"], default="claude")
    args = p.parse_args()

    tracer = setup_tracing()
    judge = ClaudeJudge() if args.judge == "claude" else ExactMatchJudge()
    evaluator = Evaluator(build_sample_workflow(tracer), judge, load_rubric(args.rubric))

    results = evaluator.run(load_cases(args.cases))
    for r in results:
        print(f"{r.case_id:20s} {r.score:.2f}  {r.output}")
    print(f"\nmean score: {sum(r.score for r in results) / max(len(results), 1):.2f} / 5")


if __name__ == "__main__":
    main()
