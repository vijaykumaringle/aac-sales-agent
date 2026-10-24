# AAC Sales Agent

A FastAPI service for capturing AAC block sales enquiries from WhatsApp, phone, or a future web intake channel. The agent records the customer details needed for human quotation review; it does not generate quotations.

## Current scope

- Health endpoint for deployment checks
- Guided, channel-agnostic intake flow for WhatsApp, phone, or web adapters
- Enquiry capture with location, project, quantity, requirement, and contact preference
- SQLite storage with staff-review status and review notes
- No quotation endpoint, price calculation, or production messaging credentials

## Project structure

```
app/
  api/routes/        HTTP endpoints
  core/              runtime configuration
  db/                SQLite setup and connections
  domain/            business entities and status values
  repositories/      database reads and writes
  schemas/           API request and response contracts
  services/          enquiry and guided intake workflows
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Database setup

The application does not create, alter, or delete database tables at startup. Configure `DATABASE_URL` to point to a database where the required tables already exist. FastAPI can start and serve `/docs` without a database connection; database connectivity is needed when using enquiry or intake endpoints.

## Test

```bash
pytest
```

## API workflow

1. A WhatsApp, phone, or web adapter passes each customer reply to `POST /intake/messages`.
2. The intake service gathers customer name, location, project type, quantity, and requirements.
3. A completed conversation becomes an enquiry with `pending_review`; it has no quotation endpoint.
4. Staff use `GET /enquiries` and `PATCH /enquiries/{id}/review` to manage follow-up.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/intake/messages` | Accept one normalized inbound message and return the next intake prompt. |
| `POST` | `/enquiries` | Create an enquiry directly (for staff or a web form). |
| `GET` | `/enquiries` | List enquiries; filter with `?status=pending_review`. |
| `GET` | `/enquiries/{id}` | Read one enquiry. |
| `PATCH` | `/enquiries/{id}/review` | Update status and staff-only review notes. |

The `/intake/messages` endpoint is intentionally provider-neutral. A production WhatsApp adapter should validate webhook signatures, translate provider payloads into the normalized request format, and send `reply_text` through the provider API.

## Next steps

1. Add a verified WhatsApp Business webhook adapter.
2. Add a phone-call provider and transcript-to-intake adapter.
3. Add staff authentication, a review dashboard, and a production database.
