# Multi-Agent Evaluation Framework

A minimal Python framework for evaluating multi-agent **LangGraph** workflows.

- **LLM-as-judge** scoring with Claude against configurable, weighted rubrics (`rubrics.yaml`)
- **OpenTelemetry** spans for every eval run, case, judge call and graph node
- **PostgreSQL** storage of per-case outputs, scores and judge reasoning (`eval_results` table)

## Quickstart

Requires Python 3.11+.

```bash
docker compose up -d            # Postgres + Jaeger (traces at http://localhost:16686)
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env && export $(grep -v '^#' .env | xargs)

agent-eval --judge exact        # offline smoke test, no API key needed
agent-eval                      # LLM-as-judge with Claude (needs ANTHROPIC_API_KEY)
```

`POSTGRES_DSN` and `OTEL_EXPORTER_OTLP_ENDPOINT` are optional; without them results are only printed and spans aren't exported (`AGENT_EVAL_CONSOLE_TRACES=1` prints them).

## Evaluating your own workflow

```python
from agent_eval.judge import ClaudeJudge
from agent_eval.rubrics import load_cases, load_rubric
from agent_eval.runner import Evaluator

evaluator = Evaluator(my_compiled_graph, ClaudeJudge(), load_rubric("rubrics.yaml"),
                      input_key="question", output_key="answer")
results = evaluator.run(load_cases("my_cases.yaml"))
```

## Layout

```
src/agent_eval/
  rubrics.py          # rubric + case loading
  judge.py            # ClaudeJudge (LLM-as-judge), ExactMatchJudge, weighted scoring
  runner.py           # Evaluator: run graph → judge → store, with spans
  tracing.py          # OpenTelemetry setup + node wrapper
  store.py            # Postgres results store
  sample_workflow.py  # two-agent demo graph
  cli.py
```
