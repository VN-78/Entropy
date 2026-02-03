# Entropy

## Project Overview

**Entropy** is a Python-based monorepo project managed with `uv`. It appears to be a system designed for data processing and analysis, utilizing the Model Context Protocol (MCP) to expose tools for AI agents or other clients.

The project consists of:
- **Core Application**: A FastAPI-based backend (`app/`).
- **MCP Servers**: Specialized servers for distinct tasks:
    - `data-refinery`: Handles data inspection, cleaning, and SQL querying via DuckDB and Pandas.
    - `visualizer`: (Likely) Handles data visualization tasks.

## Key Technologies

- **Language**: Python 3.14+
- **Package Manager**: `uv` (supports workspaces)
- **Web Framework**: FastAPI
- **MCP Framework**: `fastmcp`
- **Data Processing**: Pandas, DuckDB, PyArrow
- **Database**: SQLAlchemy, AsyncPG, Alembic (migrations)
- **Testing**: Pytest

## Architecture

The project follows a modular architecture:

- **Monorepo Structure**: Defined in `pyproject.toml` using `[tool.uv.workspace]`.
- **Clean Architecture (Data Refinery)**:
    - `domain/`: Contains business logic, models (Pydantic), and interfaces.
    - `infrastructure/`: Implementations of interfaces (e.g., `PandasDatasetClient`, `DuckDBClient`).
    - `application/`: Application entry points and server configuration.

## Building and Running

### Prerequisites

- **Python 3.14+**
- **uv**: Ensure `uv` is installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

### Setup

1.  **Install Dependencies**:
    ```bash
    uv sync
    ```

### Running Components

**Data Refinery MCP Server:**
To run the data refinery server (std transport):
```bash
uv run -p mcp-servers/data-refinery/src/data_refinery/application/server.py
# Or if installed as a module:
# uv run python -m data_refinery.application.server
```

**Main Application:**
(Assumed based on `main.py` and `app/` structure)
```bash
uv run main.py
# OR
uv run uvicorn app.main:app --reload
```

## Development Conventions

- **Type Safety**: The codebase uses strict type hinting (`py.typed`).
- **Dependency Management**: All dependencies are managed via `uv` and locked in `uv.lock`.
- **MCP Tools**: Tools exposed by MCP servers MUST have detailed docstrings explaining arguments, return types, and critical usage constraints (e.g., `clean_dataset`, `run_sql_query`).
- **Testing**: Tests are located in `test/` (global) or `mcp-servers/*/test/` (component-specific). Run with `uv run pytest`.

## Directory Structure

```text
/
├── app/                  # Main FastAPI application
├── mcp-servers/          # Independent MCP server modules
│   ├── data-refinery/    # Data cleaning and SQL server
│   └── visualizer/       # Visualization server
├── test/                 # Integration tests and test data
├── pyproject.toml        # Root workspace configuration
└── uv.lock               # Pinned dependencies
```
