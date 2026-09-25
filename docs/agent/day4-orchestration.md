# Day 4 - Planning and Governed Orchestration

Day 4 connects the deterministic tools created in Days 1-3 into an auditable question-to-plan-to-evidence workflow.

## Flow

    Natural-language question
              |
              v
       RuleBasedPlanner
              |
              v
         QueryPlan
              |
       +------+------+
       |             |
       v             v
    KPI metadata   Semantic metadata
       |             |
       +------+------+
              |
              v
        AgentResponse

Database execution remains opt-in. This is intentional: a question must first be grounded in governed business and semantic metadata before later stages generate analytical SQL.

## Why a rule-based planner first?

The planner provides a deterministic baseline for evaluation. It lets the project prove routing, grounding, failure handling and tool execution independently of an LLM provider. A later LLM planner can be compared against this baseline rather than replacing engineering controls with prompt behavior.

## Current routing

Questions about sales, revenue, margin, profit, inventory, orders and units are routed to canonical KPI definitions. Questions about schema, tables, columns, relationships or the model are routed to semantic metadata. Unknown questions enter metadata discovery rather than inventing SQL.

## Failure behavior

Tool failures stop the plan safely and are returned as structured evidence. Missing tools do not silently fall back to guessed answers.

## Day 4 completion criteria

- explicit QueryPlan and PlanStep contracts
- deterministic planner
- orchestrator plan execution
- grounded answer synthesis
- default-agent factory
- database execution opt-in
- automated orchestration tests
