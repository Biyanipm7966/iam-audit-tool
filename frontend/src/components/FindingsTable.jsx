function badge(sev) {
  const map = { CRITICAL: "🔥 CRITICAL", HIGH: "🔴 HIGH", MEDIUM: "🟠 MEDIUM", LOW: "🟡 LOW" };
  return map[sev] || sev;
}

export default function FindingsTable({ result }) {
  if (!result) return null;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 10, padding: 16 }}>
      <h3 style={{ marginTop: 0 }}>Audit Results</h3>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", opacity: 0.85 }}>
        <div><b>Users:</b> {result.users_total}</div>
        <div><b>Flagged:</b> {result.users_flagged}</div>
        <div><b>Findings:</b> {result.findings_total}</div>
        <div><b>Risk Score:</b> {result.risk_score}</div>
      </div>

      <div style={{ marginTop: 12, overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th align="left">Severity</th>
              <th align="left">Rule</th>
              <th align="left">User</th>
              <th align="left">Detail</th>
              <th align="left">Recommendation</th>
            </tr>
          </thead>
          <tbody>
            {(result.findings || []).map((f, idx) => (
              <tr key={idx} style={{ borderTop: "1px solid #eee" }}>
                <td style={{ padding: "8px 0" }}>{badge(f.severity)} ({f.risk_points})</td>
                <td style={{ padding: "8px 0" }}>{f.rule}</td>
                <td style={{ padding: "8px 0" }}>
                  {f.name}<div style={{ opacity: 0.7 }}>{f.email}</div>
                </td>
                <td style={{ padding: "8px 0" }}>{f.detail}</td>
                <td style={{ padding: "8px 0" }}>{f.recommendation}</td>
              </tr>
            ))}
            {(!result.findings || result.findings.length === 0) && (
              <tr>
                <td colSpan={5} style={{ padding: "10px 0", opacity: 0.7 }}>
                  No findings. Nice.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
