# Contributing to the Grand Library

First off, thank you for considering contributing to the WoW Datamine Toolkit! It's people like you that make the Grand Library such a powerful tool for the community.

## 🛠️ Development Setup

To ensure a consistent development experience, we use a specific set of tools and configurations.

### Prerequisites
- **Python 3.12+** (managed via `uv`)
- **Node.js 24+** (managed via `pnpm`)
- **VS Code** (recommended)

### Installation
1. Clone the repository.
2. Run `uv sync` to set up the Python environment.
3. Run `pnpm install` in the root directory to set up development hooks (Husky).
4. Run `cd Tools/web/tui-node && pnpm install` to set up the TUI dependencies.

### IDE Integration
We provide a `.vscode/settings.json` and `.vscode/extensions.json`. When you open the project in VS Code, please install the recommended extensions. This will enable:
- **Ruff**: Automatic linting and formatting for Python.
- **Biome**: Automatic linting and formatting for TypeScript and JSON.

## 📏 Coding Standards

### General Policies
- **No `any` Typed Policy**: The use of `any` is strictly prohibited in TypeScript and Python. Use specific interfaces, types, or generics.
- **Zero Warning Policy**: Code MUST NOT produce any warnings in `pytest`, `vitest`, `ruff`, or `biome`. All warnings are treated as errors.
- **No-Force-Push Policy**: `git push --force` is strictly forbidden on shared branches.

### Python
- All code must pass `uv run manage.py lint` and `uv run manage.py format`.
- Use type hints wherever possible.
- Adhere to the PEP 8 style guide (enforced by Ruff).

### Frontend (React/Ink)
- All code must pass `pnpm biome check .` and `pnpm tsc --noEmit` in the `tui-node` directory.
- Follow the Atomic Design pattern as described in `AGENT.md`.

## 📝 Commit Guidelines

We follow the **Conventional Commits** specification. This means all commit messages should look like this:

`type(scope): description`

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries

**Example:**
`feat(orchestration): add priority queue to Courier`

## 🧪 Testing

Before submitting a PR, ensure that all tests pass the 3x stability run:
```bash
uv run manage.py test
```
This runs the full suite (94+ Python tests and all TUI tests) three times to ensure no race conditions or flaky tests are introduced. CI will automatically reject PRs that fail any of these runs.

---
*Thank you for your contribution!*
