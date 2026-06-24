# Russ preferences

## General

- Prefer practical, efficient solutions over overly clever ones.
- Favor readability and maintainability.
- Be direct and concise.
- For troubleshooting, provide step-by-step instructions.
- Ask for minimal disruption to existing code structure.

## Python

- Target Python 3.14 when practical.
- `pyproject.toml` currently declares `requires-python = '>=3.14'`; keep compatibility with 3.14+ unless explicitly
  changing project metadata.
- Follow PEP 8 and PEP 484.
- Use explicit type hints where reasonable.
- Prefer single quotes where possible.
- Use single quotes for Python string literals unless double quotes are required for readability or escaping.
- Prefer f-strings for variable interpolation.
- Use triple double quotes for docstrings.
- Match Russ's existing code style when editing code.
- Prefer docstrings and Google style descriptions to provide context for functions and methods, incorporating the Args
  and Return parameters.
- Keep `main()` clean by moving blocks into helper functions.
- Prefer readable validation and logging.
- Prefer asyncio for API-heavy workflows when it improves performance.
- Scripts should be designed to run as is, without requiring command line arguments.

## Code edits

- Show only the code that changed unless a full file is specifically requested.
- Preserve existing project conventions and helper utilities when possible.
- Avoid unnecessary rewrites.
- Prefer incremental refactors over large restructures.
- Use variable names that are descriptive but not excessively long.
- When adding new functionality, consider how it fits with existing code and utilities.

## Tools and workflow

- PyCharm is the preferred IDE/interpreter environment.
- Prefer `docker compose` over `docker-compose`.
- Prefer pandas when it is a good fit.
- On Windows, prefer Command Prompt unless PowerShell is specifically needed.
- Keep examples and commands consistent with Russ's usual style.
- For this project, prefer lightweight local workflows:
  - Create/use a virtual environment in the repo.
  - Run `pytest` for validation (for example, `pytest test_crawl.py`).
  - Keep dependencies pinned in `pyproject.toml`/`uv.lock`.

## Linting and Type Safety

- Keep runtime and `.pyi` stubs synchronized whenever signatures, properties, or return types change.
- After code edits, run lint/type checks on touched files and resolve warnings before finalizing.
- Remove temporary debug statements and commented-out fallback code before final output unless explicitly asked to keep
  them.
- Prefer small helper functions for repeated pandas scalar normalization and type-safe conversions.
- When working with DataFrame object columns, coerce values to strings before join/concatenation to avoid type warnings.
- Preserve existing public behavior unless a behavior change is explicitly requested.
- If stub files are introduced later, keep runtime and stubs synchronized.

## Path Handling

- Prefer `pathlib.Path` for readable, cross-platform path handling.
- Keep path creation and validation explicit near file IO.

## Existing Utility Modules

- When possible, reuse existing project utilities rather than creating new ones.

- Always search the repository before implementing duplicate functionality.

# Project Utilities

Prefer existing helpers before creating new code.

Common utilities:

- `requests` for straightforward HTTP calls.
- `aiohttp` for async/multi-request crawling workflows.
- `beautifulsoup4` for parsing and extracting links/content.

## Logging

- Logging should be:
    - Informative
    - Minimal
    - Structured

- Prefer existing project logging utilities or decorators.

- Avoid excessive debug prints.

## Crawler Context

- This repository is for home/hobby web crawling and learning-focused automation.
- Prefer practical defaults over enterprise-grade complexity.
- Scripts should still handle common real-world issues:
  - request timeouts and retries
  - polite crawl behavior (reasonable request pacing)
  - partial failures reported clearly without crashing entire runs

## Writing style

- Avoid unnecessary filler and teaser endings.
- Share relevant advice directly when it helps.
- Opinions are welcome if they are practical and clearly grounded.

## Agent Behavior

- Agents should behave as a collaborative developer, not a generic assistant.

- They should:
    - respect repository conventions
    - understand the home/hobby crawler context
    - build upon existing work
    - avoid introducing unnecessary complexity
