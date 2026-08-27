import { useEffect, useState } from "react";
import { fetchProfile } from "../api/predictClient";

function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString("en-LK", {
    timeZone: "Asia/Colombo",
    year: "numeric", month: "long", day: "numeric",
  });
}

export default function ProfileView({ onSessionExpired }) {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfile()
      .then(setProfile)
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
        Could not load profile: {error}
      </div>
    );
  }

  if (!profile) {
    return <p className="text-sm text-[var(--ink-soft)]">Loading profile...</p>;
  }

  const initial = profile.email.charAt(0).toUpperCase();

  return (
    <div className="bg-[var(--panel)] rounded-lg border border-[var(--border)] p-8">
      <h2 className="font-display text-xl mb-6">Profile</h2>

      <div className="flex items-center gap-4 mb-8">
        <div className="w-14 h-14 rounded-full bg-[var(--teal)] text-white flex items-center justify-center
                        font-display text-2xl font-bold shrink-0">
          {initial}
        </div>
        <div>
          <div className="font-medium text-[var(--ink)]">{profile.email}</div>
          <div className="text-sm text-[var(--ink-soft)]">Clinical Staff account</div>
        </div>
      </div>

      <div className="border-t border-[var(--border)] pt-6">
        <dl className="space-y-4">
          <div className="flex justify-between text-sm">
            <dt className="text-[var(--ink-soft)]">Email</dt>
            <dd className="text-[var(--ink)] font-medium">{profile.email}</dd>
          </div>
          <div className="flex justify-between text-sm">
            <dt className="text-[var(--ink-soft)]">Account ID</dt>
            <dd className="text-[var(--ink)] font-mono">{profile.id}</dd>
          </div>
          <div className="flex justify-between text-sm">
            <dt className="text-[var(--ink-soft)]">Member since</dt>
            <dd className="text-[var(--ink)] font-medium">{formatDate(profile.created_at)}</dd>
          </div>
        </dl>
      </div>

      <p className="text-xs text-[var(--ink-soft)] mt-8 pt-4 border-t border-[var(--border)]">
        MediAlert has a single account type - every authenticated user has identical access to
        assessments, history, and the dashboard. There is no role or permission distinction between
        accounts.
      </p>
    </div>
  );
}
