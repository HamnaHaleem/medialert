import { useState } from "react";
import { loginUser } from "../api/predictClient";

export default function LoginPage({ onLoginSuccess, onGoToRegister, onGoHome }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await loginUser(email, password);
      onLoginSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--paper)] flex items-center justify-center px-6">
      <div className="max-w-sm w-full">
        <button onClick={onGoHome} className="text-sm text-[var(--teal)] hover:underline mb-6">
          ← Back to MediAlert
        </button>

        <div className="bg-[var(--panel)] border border-[var(--border)] rounded-lg p-8">
          <h1 className="font-display text-xl mb-6">Log in</h1>

          {error && (
            <div className="rounded-md border border-[var(--risk-high)] bg-[var(--risk-high-bg)] p-3 text-sm mb-5">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <label className="block mb-4">
              <span className="text-sm font-medium text-[var(--ink)]">Email</span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-[var(--teal)] focus:border-transparent"
              />
            </label>

            <label className="block mb-6">
              <span className="text-sm font-medium text-[var(--ink)]">Password</span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-[var(--teal)] focus:border-transparent"
              />
            </label>

            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-md bg-[var(--teal)] text-white font-medium py-2.5
                         hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {submitting ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className="text-sm text-[var(--ink-soft)] mt-6 text-center">
            No account yet?{" "}
            <button onClick={onGoToRegister} className="text-[var(--teal)] hover:underline">
              Create one
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
