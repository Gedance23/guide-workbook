# AI-SDLC Workflow Guardrails & Router

## Context Loading Priority
1. docs/TASKS.md (Establish current phase check)
2. docs/PROJECT.md (Review technical dependencies and structures)
3. docs/specs/ (Read target executable specification rules)
4. skills/ai-sdlc-[phase] (Execute phase instructions)

## Operating Principles
- Never write application code before tests are declared (Strict TDD).
- Inward dependencies only: Domain layer must remain pure Python code, free from frameworks (FastAPI, Pandas, or SQLAlchemy).
- Maintain structural state tracking at all boundaries.
