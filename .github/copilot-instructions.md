# Copilot Instructions

This repository is a backend project. GitHub Copilot should provide code completion and suggestions based on the following technology stack and development policies.

## Technology Stack

- **Language & Framework**: Python + FastAPI  
- **Environment Variable Management**: Pydantic (using `BaseSettings`)  
- **Database**: PostgreSQL and MongoDB
- **Object Storage**: MinIO
- **LLM Integration**: Chain processing using Google Gemini API

## Project Structure

The project is structured as follows:

```
app/
  api/
    dependencies/    # Dependencies (auth, etc.)
    v1/
      endpoints/     # API endpoint implementations
      api.py         # API router configuration
  core/
    config.py        # Configuration management
    llm/             # LLM-related modules
      chain/         # Chain processing
      client/        # LLM clients
  models/            # Data models
  schemas/           # Pydantic schemas
  services/          # Business logic
```

## Development Policies

- Code should have a **simple and clear structure**, following FastAPI's **dependency injection (Depends) and routing configuration** design principles.
- Environment variables should be securely managed using Pydantic's `BaseSettings` class.
- Use `asyncpg` or `sqlalchemy` with async support for PostgreSQL operations.
- Use `motor` (async MongoDB driver) for MongoDB operations.
- Use `minio` Python client for object storage operations.
- API endpoints should use **asynchronous functions (async def)** with appropriate `await` statements.
- Use proper abstraction layers for LLM communication, keeping separation between core logic and external services.
- Implement proper connection pooling for both PostgreSQL and MongoDB.

## Additional Guidelines

- Utilize FastAPI's `APIRouter` to organize routes by module.
- Use FastAPI's `HTTPException` for error handling.
- Initialize database connections and MinIO client only once and design them to be reusable.
- Include security measures (CORS, authentication, etc.) in code proposals.
- When writing tests, use `pytest` and `pytest-asyncio` for asynchronous testing.
- Use database transactions appropriately for PostgreSQL operations.
- Implement proper error handling for database and storage operations.
- The project supports Docker-based environment setup and Kubernetes deployment configuration.