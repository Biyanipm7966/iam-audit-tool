import { useState } from "react";
import UploadPanel from "./components/UploadPanel";
import FindingsTable from "./components/FindingsTable";

export default function App() {
  const [result, setResult] = useState(null);

  return (
    <div style={{ maxWidth: 1100, margin: "24px auto", padding: "0 16px" }}>
      <h1 style={{ marginBottom: 6 }}>Automated IAM Audit Tool</h1>
      <div style={{ opacity: 0.75, marginBottom: 18 }}>
        Detect over-privileged access, dormant accounts, missing MFA, and risky identities — export compliance-ready reports.
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 16 }}>
        <UploadPanel onResult={(r) => setResult(r)} />
        <FindingsTable result={result} />
      </div>
    </div>
  );
}
