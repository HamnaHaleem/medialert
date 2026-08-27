import { useEffect, useState } from "react";
import { fetchDashboard } from "../api/predictClient";

const RISK_STYLES = {
  Low: { text: "var(--risk-low)", bg: "var(--risk-low-bg)" },
  Medium: { text: "var(--risk-medium)", bg: "var(--risk-medium-bg)" },
  High: { text: "var(--risk-high)", bg: "var(--risk-high-bg)" },
};

function StatCard({ label, value, color }) {
  return (
    <div className="rounded-md border border-[var(--border)] p-5">
      <div className="text-xs uppercase tracking-wide text-[var(--ink-soft)] mb-2">{label}</div>
      <div className="font-display text-3xl" style={color ? { color } : undefined}>{value}</div>
    </div>
  );
}

function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleString("en-LK", {
    timeZone: "Asia/Colombo",
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

export default function DashboardView({ onSessionExpired }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboard()
      .then(setData)
      .catch((err) => {
        if (err.name === "SessionExpiredError" && onSessionExpired) {
          onSessionExpired();
        } else {
          setError(err.message);
        }
      });
  }, [onSessionExpired]);

  if (error) {
    return (
      <div className="rounded-md border border-[var(--risk-high)] bg-[var(--risk-high-bg)] p-4 text-sm">
        Could not load dashboard: {error}
      </div>
    );
  }

  if (!data) {
    return <p className="text-sm text-[var(--ink-soft)]">Loading dashboard...</p>;
  }

  if (data.total_assessments === 0) {
    return (
      <div className="bg-[var(--panel)] rounded-lg border border-[var(--border)] p-8">
        <h2 className="font-display text-xl mb-2">Dashboard</h2>
        <p className="text-sm text-[var(--ink-soft)]">
          No assessments have been recorded yet. Once assessments are submitted, summary
          statistics will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-[var(--panel)] rounded-lg border border-[var(--border)] p-8">
      <h2 className="font-display text-xl mb-6">Dashboard</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total assessments" value={data.total_assessments} />
        <StatCard label="Low risk" value={data.low_risk_count} color={RISK_STYLES.Low.text} />
        <StatCard label="Medium risk" value={data.medium_risk_count} color={RISK_STYLES.Medium.text} />
        <StatCard label="High risk" value={data.high_risk_count} color={RISK_STYLES.High.text} />
      </div>

      <div className="mb-8">
        <div className="text-xs uppercase tracking-wide text-[var(--ink-soft)] mb-2">
          Risk tier distribution
        </div>
        <div className="flex h-6 rounded-sm overflow-hidden border border-[var(--border)]">
          {data.low_risk_count > 0 && (
            <div
              style={{
                width: `${(data.low_risk_count / data.total_assessments) * 100}%`,
                backgroundColor: RISK_STYLES.Low.text,
              }}
            />
          )}
          {data.medium_risk_count > 0 && (
            <div
              style={{
                width: `${(data.medium_risk_count / data.total_assessments) * 100}%`,
                backgroundColor: RISK_STYLES.Medium.text,
              }}
            />
          )}
          {data.high_risk_count > 0 && (
            <div
              style={{
                width: `${(data.high_risk_count / data.total_assessments) * 100}%`,
                backgroundColor: RISK_STYLES.High.text,
              }}
            />
          )}
        </div>
      </div>

      <div>
        <div className="text-xs uppercase tracking-wide text-[var(--ink-soft)] mb-2">
          Recent assessments
        </div>
        <div className="border-t border-[var(--border)]">
          {data.recent_assessments.map((r) => (
            <div
              key={r.assessment_id}
              className="flex items-center justify-between py-3 border-b border-[var(--border)]"
            >
              <span className="text-sm text-[var(--ink-soft)]">{formatDate(r.created_at)}</span>
              <span className="text-sm font-medium" style={{ color: RISK_STYLES[r.risk_level]?.text }}>
                {r.risk_level}
              </span>
              <span className="font-mono text-xs text-[var(--ink-soft)]">
                {(r.readmission_probability * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
