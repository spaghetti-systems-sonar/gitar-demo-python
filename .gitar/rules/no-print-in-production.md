---
title: "Flag print() calls in production Python code"
description: "This service uses structured logging. Any print() call left in a production file should be replaced with a logger call before merge."
when: "A pull request adds or modifies a line that contains a top-level Python print( call inside any .py file outside of tests/, scripts/, or files matching *_test.py / conftest.py."
actions: "Post an inline review comment on each added print() line with the exact body: 'Replace `print(...)` with `app.logger.info(...)` (or appropriate level). This service uses Flask's structured logger; print writes to stdout and bypasses log levels, formatters, and aggregation.' Tag the comment as a Bug-severity finding. Do not block merge — surface it as a required-fix Suggestion that the author must resolve or explicitly dismiss."
---

# Details

## Why this rule exists

`print()` output goes directly to stdout without level, timestamp, request id, or structured fields. It bypasses every layer of our observability stack (Datadog ingestion, log-based alerting, the redaction filter for PII). A `print()` that survives review becomes a silent gap in production logs.

## Scope

- **In scope**: any `.py` file under the repo root that is not in an excluded path.
- **Excluded paths**: `tests/`, `scripts/`, anything matching `*_test.py`, `conftest.py`, and `__main__.py`.
- **In scope only for added/modified lines**: do not comment on `print(` calls that existed before this PR.

## Matching

Match the regex `^\s*print\s*\(` on added lines (so `# print(...)` in a comment and `myprint(...)` are not matched). String literals like `"print(...)"` are also not matched because they don't begin with the bare token at the start of the line.

## Comment text — exact

The inline comment body must be exactly:

> Replace `print(...)` with `app.logger.info(...)` (or appropriate level). This service uses Flask's structured logger; print writes to stdout and bypasses log levels, formatters, and aggregation.

Do not paraphrase. Consistent wording lets us search PRs for rule-driven comments later.

## Severity

- Inline comment severity: **Bug**.
- Not a merge blocker. Surfaces as a required-acknowledgement Suggestion: the author must reply, apply a fix, or dismiss with a reason.

## Duplicate suppression

If the same `(file, line, marker)` has already received this comment on a prior PR revision, do not post a duplicate. If the line was deleted in a later revision, mark the prior comment as resolved.
