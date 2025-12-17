import { useState } from "react";
import { getDemoUsers, runAudit, getCsvReport } from "../api";

export default function UploadPanel({ onResult }) {
  const [jsonText, setJsonText] = useState("");
  const [status, setStatus] = useState(null);

  async function loadDemo() {
    const res = await getDemoUsers();
    setJsonText(JSON.stringify(res.users, null, 2));
  }

  async function doAudit() {
    setStatus(null);
    let users;
    try {
      users = JSON.parse(jsonText);
      if (!Array.isArray(users)) throw new Error("Root must be an array of users");
    } catch (e) {
      setStatus({ type: "error", msg: e.message });
      return;
    }

    const result = await runAudit(users);
    onResult(result, users);
    setStatus({ type: "success", msg: `Audited ${result.users_total} users → ${result.findings_total} findings` });
  }

  async function downloadCsv() {
    let users;
    try {
      users = JSON.parse(jsonText);
      if (!Array.isArray(users)) throw new Error();
    } catch {
      setStatus({ type: "error", msg: "Invalid JSON for report" });
      return;
    }

    const r = await getCsvReport(users);
    const blob = new Blob([r.csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = r.filename || "iam_audit_report.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 10, padding: 16 }}>
      <h3 style={{ marginTop: 0 }}>IAM Input</h3>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Paste a JSON array of users (id, email, roles, groups, mfa_enabled, last_login_days…).
      </p>

      <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
        <button onClick={loadDemo}>Load Demo Users</button>
        <button onClick={doAudit}>Run Audit</button>
        <button onClick={downloadCsv}>Download CSV Report</button>
      </div>

      <textarea
        value={jsonText}
        onChange={(e) => setJsonText(e.target.value)}
        rows={14}
        style={{ width: "100%", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}
        placeholder='[{"id":"u-001","name":"...","email":"...","roles":["Admin"],"mfa_enabled":true,"last_login_days":5}]'
      />

      {status && (
        <div style={{ marginTop: 10, fontWeight: 600 }}>
          {status.type === "error" ? "❌ " : "✅ "}
          {status.msg}
        </div>
      )}
    </div>
  );
}
