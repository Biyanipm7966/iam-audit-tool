from typing import Dict, List, Any, Tuple

# Basic risk scoring (tune as you like)
SEVERITY_POINTS = {
    "CRITICAL": 10,
    "HIGH": 7,
    "MEDIUM": 4,
    "LOW": 2,
}

PRIVILEGED_ROLE_KEYWORDS = ["admin", "owner", "superuser", "root"]
SENSITIVE_ROLE_KEYWORDS = ["finance", "hr", "payroll", "billing", "security"]

def _has_keyword(items: List[str], keywords: List[str]) -> bool:
    s = " ".join(items).lower()
    return any(k in s for k in keywords)

def evaluate_user(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    roles = user.get("roles", []) or []
    groups = user.get("groups", []) or []
    user_type = (user.get("user_type") or "employee").lower()

    is_active = bool(user.get("is_active", True))
    mfa = bool(user.get("mfa_enabled", False))
    last_login_days = int(user.get("last_login_days", 999999))

    # Rule 1: Privileged role (Admin/Owner/etc.)
    if _has_keyword(roles, PRIVILEGED_ROLE_KEYWORDS) or _has_keyword(groups, PRIVILEGED_ROLE_KEYWORDS):
        findings.append({
            "severity": "HIGH",
            "rule": "Privileged access detected",
            "detail": f"User has privileged role/group. Roles={roles} Groups={groups}",
            "recommendation": "Validate business need; enforce least privilege; time-bound admin access.",
        })

    # Rule 2: Contractor with admin
    if user_type == "contractor" and (_has_keyword(roles, PRIVILEGED_ROLE_KEYWORDS) or _has_keyword(groups, PRIVILEGED_ROLE_KEYWORDS)):
        findings.append({
            "severity": "CRITICAL",
            "rule": "Contractor has privileged access",
            "detail": f"Contractor account has privileged permissions. Roles={roles}",
            "recommendation": "Remove admin rights; use JIT access; require manager approval & logging.",
        })

    # Rule 3: No MFA
    if is_active and not mfa:
        findings.append({
            "severity": "HIGH" if _has_keyword(roles, PRIVILEGED_ROLE_KEYWORDS) else "MEDIUM",
            "rule": "MFA not enabled",
            "detail": "Account is active but MFA is disabled.",
            "recommendation": "Enable MFA and enforce conditional access policies.",
        })

    # Rule 4: Dormant but active account
    if is_active and last_login_days >= 90:
        findings.append({
            "severity": "MEDIUM" if last_login_days < 180 else "HIGH",
            "rule": "Dormant active account",
            "detail": f"Last login was {last_login_days} days ago.",
            "recommendation": "Disable account or require re-verification; review access and roles.",
        })

    # Rule 5: Sensitive roles (Finance/HR/etc.)
    if _has_keyword(roles, SENSITIVE_ROLE_KEYWORDS) or _has_keyword(groups, SENSITIVE_ROLE_KEYWORDS):
        findings.append({
            "severity": "MEDIUM",
            "rule": "Sensitive data access",
            "detail": f"User has access to sensitive functions. Roles={roles} Groups={groups}",
            "recommendation": "Ensure access is approved; add periodic access reviews & logging.",
        })

    # Rule 6: Shared/service account without hardening
    email = (user.get("email") or "").lower()
    name = (user.get("name") or "").lower()
    if user_type in ("service", "shared") or "shared" in email or "shared" in name:
        if not mfa:
            findings.append({
                "severity": "HIGH",
                "rule": "Shared/service account without MFA",
                "detail": "Shared/service account detected with MFA disabled.",
                "recommendation": "Convert to managed identity/service principal; rotate secrets; enforce MFA where applicable.",
            })

    return findings

def audit(users: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_findings = []
    total_risk = 0
    users_flagged = 0

    for u in users:
        user_findings = evaluate_user(u)
        if user_findings:
            users_flagged += 1

        # attach user info to each finding
        for f in user_findings:
            points = SEVERITY_POINTS.get(f["severity"], 1)
            total_risk += points
            all_findings.append({
                "user_id": u.get("id", ""),
                "name": u.get("name", ""),
                "email": u.get("email", ""),
                "department": u.get("department", ""),
                "user_type": u.get("user_type", ""),
                **f,
                "risk_points": points,
            })

    # Simple maturity summary
    privileged_count = sum(1 for f in all_findings if f["rule"] in ("Privileged access detected", "Contractor has privileged access"))
    no_mfa_count = sum(1 for f in all_findings if f["rule"] == "MFA not enabled")

    return {
        "users_total": len(users),
        "users_flagged": users_flagged,
        "findings_total": len(all_findings),
        "risk_score": total_risk,
        "summary": {
            "privileged_access_findings": privileged_count,
            "mfa_missing_findings": no_mfa_count,
        },
        "findings": sorted(all_findings, key=lambda x: x["risk_points"], reverse=True),
    }
