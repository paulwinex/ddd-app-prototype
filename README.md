# DDD Arch Prototype

DDD Architecture Prototype with FastAPI implementing the example domains.

```
DOMAIN/                        # domain root
├── domain/                    # domain layer
│   ├── entities/              # domain entities
│   ├── value_objects/         # calue objects
│   ├── aggregates/            # domain aggregates
│   ├── interfaces/            # repository protocols
│   ├── events/                # domain events
│   └── exceptions.py          # domain exceptions
│
├── dto/                       # data Transfer Objects
│
├── mappers/                   # entity-DTO mappers
│
├── application/               # application layer
│   ├── services/              # use cases
│   │   ├── commands/          # command handlers
│   │   └── queries/           # query handlers
│
├── infra/                     # infrastructure layer
│   ├── models/                # SQLAlchemy ORM models
│   ├── repositories/          # repository implementations
│   └── dependencies.py        # DI dependencies
│
└── api/                       # API layer
    ├── schemas.py             # Pydantic schemas
    ├── dependencies.py        # API dependencies
    └── v1/                    # API version 1
        └── domain_router.py   # endpoints
```

## Tech Stack

- **Python 3.14**
- **uv** - Package manager
- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - ORM with async support
- **PostgreSQL** - Database (via asyncpg)
- **Pydantic** - Data validation
- **Pydantic Settings** - Configuration management
- **python-jose** - JWT tokens

TODO
- **FastStream** - Message broker (NATS/Kafka)
- **Taskiq** - Background tasks


### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd celan_arch_prototype
```

Install `just` (Optional)
https://github.com/casey/just?tab=readme-ov-file#installation

2. Install dependencies (for local running)

```bash
just install
```
Or:
```bash
uv sync --dev
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your settings:
```env
APP_NAME=celan_arch_prototype
APP_DEBUG=true

APP_DB_HOST=localhost
APP_DB_PORT=5432
APP_DB_NAME=app_db
APP_DB_USER=app_user
APP_DB_PASSWORD=password

APP_AUTH_JWT_SECRET=your-secret-key-change-in-production
```

### Running the Application

Using just:
```bash
just run
```

Or directly with uv:
```bash
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

Build and run:
```bash
just docker-build
just docker-run
```


## License

MIT
