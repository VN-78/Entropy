# Entropy

## Project Overview

**Entropy** is an AI-powered data analysis and refinery platform. It enables users to interact with datasets (CSV, Parquet) using natural language, leveraging Large Language Models (LLMs) and the Model Context Protocol (MCP) to perform complex data operations like inspection, cleaning, and SQL-based transformations.

The project is structured as a monorepo managed with `uv`.

## Core Components

- **Main Backend (`app/`)**: A FastAPI application that serves as the orchestration layer.
    - **LLM Integration**: Interfaces with local LLM providers (e.g., LM Studio) to handle natural language processing.
    - **Storage**: Manages file uploads and artifacts using S3-compatible storage (MinIO/AWS S3).
    - **API**: Provides endpoints for chat completions and file management.
- **Data Refinery MCP Server (`mcp-servers/data-refinery`)**: A specialized service that exposes data processing tools via MCP.
    - **DuckDB**: For high-performance SQL querying directly on files.
    - **Pandas**: For data inspection and complex cleaning operations.
- **Visualizer MCP Server (`mcp-servers/visualizer`)**: (Placeholder) Planned for automated data visualization.

## Key Technologies

- **Language**: Python 3.14+
- **Package Manager**: `uv` (workspace mode)
- **Web Framework**: FastAPI
- **LLM Connectivity**: LM Studio (OpenAI-compatible API)
- **Data Stack**: Pandas, DuckDB, PyArrow
- **Storage**: Boto3 (S3/MinIO)
- **Protocol**: Model Context Protocol (MCP) via `fastmcp`

## Architecture & Design Patterns

- **Clean Architecture**: Applied particularly in the `data-refinery` server, separating domain logic from infrastructure (DuckDB/Pandas implementations).
- **Pass-by-Reference Tooling**: MCP tools operate on file URIs and return new file URIs for intermediate results, rather than passing large dataframes in memory.
- **Prompt Templating**: Managed centrally in `app/core/templates.py` to ensure consistent LLM behavior.

## Workflow

1.  **Data Ingestion**: Datasets are uploaded to S3 storage.
2.  **Tool Discovery**: The system identifies available MCP tools (`inspect_dataset`, `run_sql_query`, `clean_dataset`).
3.  **LLM Orchestration**: The user provides a natural language query. The LLM selects and chains appropriate tools to fulfill the request.
4.  **Artifact Generation**: Operations like cleaning or querying produce new files in storage, which are then used for subsequent steps.

## Development Status

- [x] FastAPI Backend Skeleton
- [x] S3 Storage Integration
- [x] LM Studio Integration
- [x] Data Refinery MCP (Inspect, SQL, Clean)
- [ ] Visualizer MCP Implementation
- [ ] Frontend UI (React/Vite)
- [ ] Agentic Tool Selection Loop
