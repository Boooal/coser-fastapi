# Coser

SaaS-платформа для управления складом сервисных компаний, обслуживающих кофемашины и другое оборудование. Учёт запчастей, узлов, расходников и устройств, складские операции, мультитенантность.

API в RPC-стиле: только `POST`, JSON-body, единая обёртка ответа `{ok, result | error}`.

## Стек

- Python 3.13
- FastAPI
- SQLAlchemy 2.x (async) + asyncpg
- PostgreSQL 15
- Alembic
- JWT (python-jose) + bcrypt
- [uv](https://docs.astral.sh/uv/) для управления зависимостями

## Лицензия

[MIT](LICENSE)