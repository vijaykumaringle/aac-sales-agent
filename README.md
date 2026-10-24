# AAC Sales Agent

A FastAPI service for capturing AAC block sales enquiries from WhatsApp, phone, or a future web intake channel. The agent records the customer details needed for human quotation review; it does not generate quotations.

## Current scope

- Health endpoint for deployment checks
- Enquiry intake endpoint with basic contact and requirements details
- In-memory repository placeholder, designed to be replaced with a database
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

## Next steps

1. Add persistent storage for enquiries.
2. Connect a WhatsApp Business provider and map messages to the intake fields.
3. Add a staff review workflow for qualification and quotation follow-up.
