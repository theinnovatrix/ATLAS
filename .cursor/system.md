# NOVA Voice Assistant Development Agent

## Mission

Build NOVA as a production-ready Linux voice assistant with modular voice I/O, system control,
web integrations, browser automation for permitted workflows, coding assistance, a PyQt6 GUI,
tests, documentation, and deployment assets.

## Operating Rules

- Verify repository and environment state before making implementation changes.
- Prefer small, independently testable modules with typed public APIs.
- Use official APIs, documented feeds, public pages, or user-authorized exports for web and social
  data access.
- Do not bypass authentication, platform access controls, rate limits, robots restrictions, or
  private backend APIs.
- Store credentials in environment variables or ignored local config files, never source code.
- Add tests for each new module and run relevant checks before committing.
- Keep destructive system actions behind explicit safety policy and confirmation flows.

## Target Quality Gates

- Format with Black or Ruff format.
- Lint with Ruff, and add mypy where practical.
- Run pytest with coverage for implemented modules.
- Scan security-sensitive modules with Bandit.
- Document public APIs with concise Google-style docstrings.

## Initial Execution Protocol

1. Read `.cursor/repo_analysis.json`.
2. Read `.cursor/dependency_matrix.json`.
3. Read `.cursor/architecture_diagram.md`.
4. Read `.cursor/implementation_plan.md`.
5. Start with Phase 0 scaffolding only after explicit approval.

## First Implementation Milestone

Create the Python package scaffold, dependency manifests, configuration loader, structured logging,
baseline intent parser, safety policy, CLI entry point, and initial tests. Do not add heavyweight
audio, GUI, or external API dependencies until the scaffold passes its checks.
