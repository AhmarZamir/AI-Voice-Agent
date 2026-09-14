# AI Voice Agent — Patient Registration

A simple end-to-end backend for a conversational voice agent that registers patients, persists their data, and exposes REST endpoints for retrieving and updating records.

This implementation follows the supplied technical assessment architecture, with one requested adaptation: **Pakistani mobile numbers are used instead of U.S. phone numbers**.

## Architecture

```text
Caller
  ↓
Voice/Telephony Provider
  ↓
LLM Voice Agent
  ↓
FastAPI REST API
  ↓
SQLAlchemy
  ↓
SQLite / PostgreSQL
```

## Current Features

- FastAPI backend
- Persistent patient model
- Pakistani mobile-number validation and normalization
- Numbers such as `03001234567`, `923001234567`, and `+923001234567` normalize to `+923001234567`
- Create patient
- List/search patients
- Retrieve patient by UUID
- Update patient
- Soft-delete patient
- Duplicate detection by mobile number
- Pydantic server-side validation
- Health endpoint
- Voice-agent system prompt with confirmation-before-save behavior

## Important Note About Pakistani Phone Numbers

The assessment originally asks for a real U.S. phone number. This repository intentionally adapts the phone-number flow for Pakistan.

The backend fully supports Pakistani mobile numbers. Actual inbound Pakistani telephony depends on the voice provider you choose and whether that provider can provision or connect a Pakistan (+92) number. If your voice platform cannot directly provision one, connect a supported Pakistani SIP/telephony provider or use the platform's SIP/trunking option where available.

## Project Structure

```text
AI-Voice-Agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── crud.py
├── .env.example
├── .gitignore
├── requirements.txt
├── voice_agent_prompt.md
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/AhmarZamir/AI-Voice-Agent.git
cd AI-Voice-Agent
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment file

Copy `.env.example` to `.env`.

The default database is SQLite:

```env
DATABASE_URL=sqlite:///./patients.db
```

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/patients` | List/search active patients |
| GET | `/patients/{patient_id}` | Retrieve one patient |
| POST | `/patients` | Create patient |
| PUT | `/patients/{patient_id}` | Partially update patient |
| DELETE | `/patients/{patient_id}` | Soft-delete patient |

### Optional query filters

```text
GET /patients?last_name=Khan
GET /patients?phone_number=03001234567
```

## Example Patient Request

```json
{
  "first_name": "Ali",
  "last_name": "Khan",
  "date_of_birth": "1998-05-15",
  "sex": "Male",
  "phone_number": "03001234567",
  "email": "ali@example.com",
  "address_line_1": "Block 5, Clifton",
  "address_line_2": null,
  "city": "Karachi",
  "state": "Sindh",
  "zip_code": "75600",
  "insurance_provider": null,
  "insurance_member_id": null,
  "preferred_language": "Urdu",
  "emergency_contact_name": null,
  "emergency_contact_phone": null
}
```

The stored phone number will be normalized to:

```text
+923001234567
```

## Voice Agent Flow

The intended conversation flow is:

```text
Greet caller
   ↓
Collect required demographics naturally
   ↓
Validate / clarify invalid values
   ↓
Accept corrections and out-of-order information
   ↓
Read all collected information back
   ↓
Ask for explicit confirmation
   ↓
POST /patients
   ↓
Confirm success or explain failure
   ↓
End call gracefully
```

See `voice_agent_prompt.md` for the complete voice-agent behavior.

## Duplicate Detection

If an active patient already exists with the same normalized phone number, `POST /patients` returns HTTP `409 Conflict` with the existing patient identifier and name. This allows the voice agent to offer an update instead of creating a duplicate record.

## Database

SQLite is used by default because it is simple and persistent for the assessment. For deployment, set `DATABASE_URL` to a PostgreSQL connection string if desired.

## Deployment

The FastAPI service can be deployed on Render, Railway, Fly.io, or another Python-compatible host. Use the production start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Do not commit `.env` or provider API keys.

## Voice Provider Integration — Next Step

The next implementation step is to connect a voice platform such as Retell/Vapi or another provider to this API. Configure a tool/function called `create_patient` that sends the confirmed registration payload to:

```text
POST https://YOUR-LIVE-API/patients
```

For a Pakistani inbound number, choose a provider or SIP setup that supports Pakistan (+92), then route that number to the configured voice agent.

## Known Limitations / Next Steps

- Telephony provider is not configured in code yet.
- Live Pakistani number provisioning depends on the selected provider.
- `state` and `zip_code` field names are retained from the assessment for API compatibility even though Pakistani addresses are better described as province/region and postal code.
- Automated API tests should be added next.
- Production deployments should use PostgreSQL instead of a local SQLite file where persistence across ephemeral deployments is required.
