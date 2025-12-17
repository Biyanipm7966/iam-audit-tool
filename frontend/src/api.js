const API_BASE = "http://localhost:8002";

export async function getDemoUsers() {
  const res = await fetch(`${API_BASE}/api/demo`);
  if (!res.ok) throw new Error("Failed to load demo users");
  return res.json();
}

export async function runAudit(users) {
  const res = await fetch(`${API_BASE}/api/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ users }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Audit failed");
  return res.json();
}

export async function getCsvReport(users) {
  const res = await fetch(`${API_BASE}/api/audit/report.csv`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ users }),
  });
  if (!res.ok) throw new Error("Report failed");
  return res.json();
}
