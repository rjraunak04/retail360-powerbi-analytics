# Day 5 - Production Guardrails

Day 5 hardens the boundary between future model-generated SQL and PostgreSQL.

## Defense in depth

Retail360 does not rely on a prompt such as "only generate safe SQL." The execution path now applies deterministic controls before a query reaches PostgreSQL:

1. one statement only
2. SELECT or WITH only
3. SQL comments rejected
4. mutating and administrative keywords rejected
5. dangerous PostgreSQL file, delay and external-access functions rejected
6. analytics schema allow-list
7. analytics table allow-list
8. query-length boundary
9. database transaction forced read-only
10. server-side statement timeout
11. bounded returned rows
12. database failures sanitized before returning to the agent

## Why comments are rejected

Comments can be used to hide or alter the apparent structure of generated SQL. Agent queries do not need comments, so the safest contract is to reject them.

## Why strings are treated separately

Safety keyword checks ignore ordinary quoted string literals. A legitimate query can therefore contain text such as "drop table" without being mistaken for executable SQL.

## Table allow-list

The configured tables are the governed Retail360 dimensions and facts. An agent cannot query a newly created or unrelated table merely because it exists in the analytics schema.

## Adversarial tests

The Day 5 suite includes multi-statement attempts, non-approved schemas and tables, comments, dangerous PostgreSQL functions, mutation attempts, query-size abuse, and sensitive error-message checks.

These controls complement least-privilege database credentials; they do not replace database permissions.
