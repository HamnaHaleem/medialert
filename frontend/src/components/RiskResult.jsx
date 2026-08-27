import { useState } from "react";
import { downloadPdf } from "../api/predictClient";

const RISK_STYLES = {
  Low: { text: "var(--risk-low)", bg: "var(--risk-low-bg)" },
  Medium: { text: "var(--risk-medium)", bg: "var(--risk-medium-bg)" },
  High: { text: "var(--risk-high)", bg: "var(--risk-high-bg)" },
};

function FactorCard({ factor, maxAbs }) {
  const isPositive = factor.contribution >= 0;
  const widthPct = maxAbs > 0 ? (Math.abs(factor.contribution) / maxAbs) * 100 : 0;
  const color = isPositive ? "var(--risk-high)" : "var(--teal)";

  return (
    <div className="py-3 border-b border-[var(--border)] last:border-b-0">
      <p className="text-sm text-[var(--ink)] mb-2">{factor.explanation}</p>
      <div className="flex items-center gap-3">
        <div className="relative h-2.5 flex-1 bg-[var(--paper)] rounded-sm overflow-hidden">
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-[var(--border)]" />
          <div
            className="absolute top-0 bottom-0 rounded-sm"
            style={{
              width: `${widthPct / 2}%`,
              left: isPositive ? "50%" : `${50 - widthPct / 2}%`,
              backgroundColor: color,
            }}
          />
        </div>
        <span className="font-mono text-xs text-[var(--ink-soft)] w-16 text-right shrink-0">
          {isPositive ? "+" : ""}{factor.contribution.toFixed(3)}
        </span>
      </div>
    </div>
  );
}

export default function RiskResult({ result, onReset, onSessionExpired }) {
  const style = RISK_STYLES[result.risk_level] ?? RISK_STYLES.Medium;
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);

  const handleDownload = async () => {
    setDownloading(true);
    setDownloadError(null);
    try {
      await downloadPdf(result.assessment_id);
    } catch (err) {
      if (err.name === "SessionExpiredError" && onSessionExpired) {
        onSessionExpired();
      } else {
        setDownloadError(err.message);
      }
    } finally {
      setDownloading(false);
    }
  };

  const probabilityPct = (result.readmission_probability * 100).toFixed(1);
  const maxAbs = Math.max(...result.top_contributing_factors.map((f) => Math.abs(f.contribution)), 0.001);

  return (
    <div className="bg-[var(--panel)] rounded-lg border border-[var(--border)] p-8">
      <div className="flex items-baseline justify-between mb-6">
        <h2 className="font-display text-xl">Risk assessment</h2>
        <button
          onClick={onReset}
          className="text-sm text-[var(--teal)] hover:underline"
        >
          New assessment
        </button>
      </div>

      <div
        className="rounded-lg p-7 mb-8 flex items-center justify-between shadow-sm"
        style={{ backgroundColor: style.text }}
      >
        <div>
          <div className="text-xs uppercase tracking-widest font-semibold text-white/75 mb-2">
            30-day readmission risk
          </div>
          <div className="font-display text-4xl font-bold text-white leading-none flex items-center gap-3">
            <span className="inline-block w-3.5 h-3.5 rounded-full bg-white/90" />
            {result.risk_level}
          </div>
        </div>
        <div className="text-right">
          <div className="font-mono text-5xl font-bold text-white leading-none">
            {probabilityPct}%
          </div>
          <div className="text-xs text-white/75 mt-1">predicted probability</div>
        </div>
      </div>

      <div>
        <h3 className="font-display text-sm tracking-wide uppercase text-[var(--ink-soft)] mb-1">
          What's driving this assessment
        </h3>
        <p className="text-xs text-[var(--ink-soft)] mb-4">
          The factors below had the largest influence on this patient's result, in plain terms.
          Bars extending right (<span style={{ color: "var(--risk-high)" }}>red</span>) push risk up;
          bars extending left (<span style={{ color: "var(--teal)" }}>teal</span>) push it down.
        </p>
        <div>
          {result.top_contributing_factors.map((f) => (
            <FactorCard key={f.feature} factor={f} maxAbs={maxAbs} />
          ))}
        </div>
      </div>

      {downloadError && (
        <p className="text-xs text-[var(--risk-high)] mt-4">{downloadError}</p>
      )}

      {result.assessment_id && (
        <div className="flex items-center justify-between mt-6">
          <p className="text-xs text-[var(--ink-soft)]">
            Assessment ID: <span className="font-mono">{result.assessment_id}</span>
          </p>
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="text-sm rounded-md border border-[var(--teal)] text-[var(--teal)] font-medium
                       px-4 py-1.5 hover:bg-[var(--teal-soft)] transition-colors disabled:opacity-50"
          >
            {downloading ? "Preparing PDF..." : "Download PDF"}
          </button>
        </div>
      )}

      <p className="text-xs text-[var(--ink-soft)] mt-4 pt-4 border-t border-[var(--border)]">
        This output is a decision-support estimate, not a diagnosis. It is intended to inform clinical
        judgment alongside the full patient record, not to replace it.
      </p>
    </div>
  );
}
