# IAM Audit Tool

A full-stack web application for auditing Identity and Access Management (IAM) configurations. Automatically detects over-privileged accounts, missing MFA, dormant users, and other risky identity patterns — and generates compliance-ready reports.

## Features

- Detects 6 categories of IAM risk (see [Audit Rules](#audit-rules))
- Risk scoring per finding (CRITICAL / HIGH / MEDIUM / LOW)
- Load demo users to explore the tool instantly
- Export findings as a CSV report
- Dark/light theme support

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Frontend | React 19, Vite, vanilla CSS |

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

API runs at `http://localhost:8002`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI runs at `http://localhost:5173`.

## Usage

1. Open the app at `http://localhost:5173`.
2. Click **Load Demo Users** to populate sample data, or paste your own JSON array into the input panel.
3. Click **Run Audit** to analyze the users.
4. Review findings in the results panel.
5. Click **Download CSV Report** to export findings.

### User Data Schema

```json
[
  {
    "id": "u-001",
    "name": "Jane Smith",
    "email": "jane@company.com",
    "department": "Engineering",
    "user_type": "employee",
    "is_active": true,
    "mfa_enabled": false,
    "last_login_days": 30,
    "roles": ["Admin"],
    "groups": ["IT-Admins"]
  }
]
```

`user_type` accepts: `employee`, `contractor`, `service`, `shared`.

## Audit Rules

| Severity | Rule | Condition |
|----------|------|-----------|
| CRITICAL | Contractor with privileged access | `user_type=contractor` + admin/owner role |
| HIGH | Privileged access detected | Any admin/owner/superuser/root role |
| HIGH | MFA not enabled (privileged user) | `is_active=true`, `mfa_enabled=false`, privileged role |
| HIGH | Shared/service account without MFA | `user_type=service/shared`, `mfa_enabled=false` |
| MEDIUM | MFA not enabled | `is_active=true`, `mfa_enabled=false` |
| MEDIUM | Dormant active account | `is_active=true`, `last_login_days >= 90` |
| MEDIUM | Sensitive data access | Roles matching finance/hr/payroll/billing/security |

### Risk Scoring

| Severity | Points |
|----------|--------|
| CRITICAL | 10 |
| HIGH | 7 |
| MEDIUM | 4 |
| LOW | 2 |

The aggregate risk score is the sum of all finding points across audited users.

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/demo` | Fetch demo user data |
| `POST` | `/api/audit` | Run audit on a user list |
| `POST` | `/api/audit/report.csv` | Download findings as CSV |

## Configuration

**Backend CORS** — edit `allow_origins` in [backend/main.py](backend/main.py) to add your frontend URL.

**Frontend API URL** — edit `API_BASE` in [frontend/src/api.js](frontend/src/api.js) to point at your backend.

## Project Structure

```
iam-audit-tool/
├── backend/
│   ├── main.py          # FastAPI app, routes, Pydantic models
│   ├── rules.py         # Audit rules and risk scoring logic
│   ├── demo_data.py     # Sample users for demo mode
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx               # Root layout
    │   ├── api.js                # API client
    │   └── components/
    │       ├── UploadPanel.jsx   # Input and controls
    │       └── FindingsTable.jsx # Results display
    └── package.json
```
