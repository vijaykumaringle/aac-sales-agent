# AAC Sales Agent

A FastAPI service for capturing AAC block sales enquiries from WhatsApp, phone, or a future web intake channel. The agent records the customer details needed for human quotation review; it does not generate quotations.

## Current scope

- Health endpoint for deployment checks
- Enquiry intake endpoint with contact, location, project, quantity, and source details
- SQLite storage with a staff-review status and notes workflow
- List, filter, and update saved enquiries through the API
- No production credentials or messaging-provider integration

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Test

```bash
pytest
```

## API workflow

1. A future WhatsApp, phone, or web adapter calls `POST /enquiries` after collecting the lead details.
2. The service saves the lead with `pending_review`; it has no quotation endpoint.
3. Staff use `GET /enquiries` and `PATCH /enquiries/{id}/review` to assign the next status and review notes.

## Next steps

1. Connect a WhatsApp Business provider and map messages to the intake fields.
2. Add a phone-call provider and transcript-to-enquiry adapter.
3. Add staff authentication and a review dashboard.
