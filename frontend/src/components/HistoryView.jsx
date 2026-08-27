import { useState } from "react";
import { fetchHistory, downloadPdf } from "../api/predictClient";

const RISK_COLORS = {
  Low: "var(--risk-low)",
  Medium: "var(--risk-medium)",
  High: "var(--risk-high)",
};

function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleString("en-LK", {
    timeZone: "Asia/Colombo",
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  }) + " (SL time)";
}

export default function HistoryView({ onSessionExpired }) {
  const [reference, setReference] = useState("");
  const [records, setRecords] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searched, setSearched] = useState("");
  const [downloadingId, setDownloadingId] = useState(null);
  const [downloadError, setDownloadError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!reference.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHistory(reference.trim());
      setRecords(data);
      setSearched(reference.trim());
    } catch (err) {
      if (err.name === "SessionExpiredError" && onSessionExpired) {
        onSessionExpired();
      } else {
        setError(err.message);
        setRecords(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (assessmentId) => {
    setDownloadingId(assessmentId);
    setDownloadError(null);
    try {
      await downloadPdf(assessmentId);
    } catch (err) {
      if (err.name === "SessionExpiredError" && onSessionExpired) {
        onSessionExpired();
      } else {
        setDownloadError(`Could not download assessment ${assessmentId}: ${err.message}`);
      }
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="bg-[var(--panel)] rounded-lg border border-[var(--border)] p-8">
      <h2 className="font-display text-xl mb-6">Patient risk history</h2>

      <form onSubmit={handleSearch} className="flex gap-3 mb-8">
        <input
          type="text"
          value={reference}
          onChange={(e) => setReference(e.target.value)}
          placeholder="Enter patient reference (e.g. hospital MRN)"
          className="flex-1 rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-[var(--teal)] focus:border-transparent"
        />
        <button
          type="submit"
          disabled={loading || !reference.trim()}
          className="rounded-md bg-[var(--teal)] text-white font-medium px-5 py-2 text-sm
                     hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && (
        <div className="rounded-md border border-[var(--risk-high)] bg-[var(--risk-high-bg)] p-4 text-sm mb-6">
          {error}
        </div>
      )}

      {downloadError && (
        <div className="rounded-md border border-[var(--risk-high)] bg-[var(--risk-high-bg)] p-4 text-sm mb-6">
          {downloadError}
        </div>
      )}

      {records && records.length === 0 && (
        <p className="text-sm text-[var(--ink-soft)]">
          No assessments found for patient reference "{searched}". This patient may not have been
          assessed yet, or the reference used at the time was entered differently.
        </p>
      )}

      {records && records.length > 0 && (
        <div>
          <p className="text-xs text-[var(--ink-soft)] mb-4 uppercase tracking-wide">
            {records.length} assessment{records.length !== 1 ? "s" : ""} for "{searched}"
          </p>
          <div className="border-t border-[var(--border)]">
            {records.map((r) => (
              <div
                key={r.assessment_id}
                className="flex items-center justify-between py-4 border-b border-[var(--border)]"
              >
                <div>
                  <div className="text-sm text-[var(--ink)]">{formatDate(r.created_at)}</div>
                  <div className="text-xs text-[var(--ink-soft)] font-mono">
                    Assessment ID: {r.assessment_id}
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div
                      className="font-display text-lg"
                      style={{ color: RISK_COLORS[r.risk_level] ?? "var(--ink)" }}
                    >
                      {r.risk_level}
                    </div>
                    <div className="font-mono text-xs text-[var(--ink-soft)]">
                      {(r.readmission_probability * 100).toFixed(1)}%
                    </div>
                  </div>
                  <button
                    onClick={() => handleDownload(r.assessment_id)}
                    disabled={downloadingId === r.assessment_id}
                    className="text-xs rounded-md border border-[var(--teal)] text-[var(--teal)] font-medium
                               px-3 py-1.5 hover:bg-[var(--teal-soft)] transition-colors
                               disabled:opacity-50 disabled:cursor-wait shrink-0"
                  >
                    {downloadingId === r.assessment_id ? "Preparing..." : "Download PDF"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
