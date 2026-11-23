"""Persist evaluation results to PostgreSQL (skipped if POSTGRES_DSN is unset)."""

import json
import os

import psycopg

SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_results (
    id          SERIAL PRIMARY KEY,
    run_id      TEXT NOT NULL,
    case_id     TEXT NOT NULL,
    output      TEXT,
    score       DOUBLE PRECISION,
    details     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


class ResultStore:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or os.getenv("POSTGRES_DSN")

    def save(self, run_id: str, case_id: str, output: str, score: float, details: dict) -> None:
        if not self.dsn:
            return
        with psycopg.connect(self.dsn) as conn:
            conn.execute(SCHEMA)
            conn.execute(
                "INSERT INTO eval_results (run_id, case_id, output, score, details) VALUES (%s, %s, %s, %s, %s)",
                (run_id, case_id, output, score, json.dumps(details)),
            )
