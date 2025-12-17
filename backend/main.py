from __future__ import annotations

import csv
import io
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rules import audit
from demo_data import DEMO_USERS

app = FastAPI(title="IAM Audit Tool API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class UserRecord(BaseModel):
    id: str
    name: str
    email: str
    department: Optional[str] = ""
    user_type: str = Field(default="employee")     # employee | contractor | service
    is_active: bool = True
    mfa_enabled: bool = False
    last_login_days: int = 999999
    roles: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)

class AuditRequest(BaseModel):
    users: List[UserRecord]

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/demo")
def demo():
    return {"users": DEMO_USERS}

@app.post("/api/audit")
def run_audit(payload: AuditRequest):
    users = [u.model_dump() for u in payload.users]
    result = audit(users)
    return result

@app.post("/api/audit/report.csv")
def audit_csv(payload: AuditRequest):
    users = [u.model_dump() for u in payload.users]
    result = audit(users)
    findings = result["findings"]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "severity","risk_points","rule","detail","recommendation",
        "user_id","name","email","department","user_type"
    ])
    writer.writeheader()
    for f in findings:
        writer.writerow({k: f.get(k, "") for k in writer.fieldnames})

    return {
        "filename": "iam_audit_report.csv",
        "csv": output.getvalue(),
        "meta": {
            "users_total": result["users_total"],
            "users_flagged": result["users_flagged"],
            "findings_total": result["findings_total"],
            "risk_score": result["risk_score"],
        }
    }
