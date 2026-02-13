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

### Python
- All code must pass `uv run manage.py lint`.
- Use type hints wherever possible.
- Adhere to the PEP 8 style guide (enforced by Ruff).

### Frontend (React/Ink)
- All code must pass `pnpm biome check .` in the `tui-node` directory.
- No `any` types allowed.
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

Before submitting a PR, ensure that all tests pass:
```bash
uv run manage.py test
```
This will run the stability suite (3x Python and TUI tests).

---
*Thank you for your contribution!*
