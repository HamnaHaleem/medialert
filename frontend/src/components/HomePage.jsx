export default function HomePage({ onGoToLogin, onGoToRegister }) {
  return (
    <div className="min-h-screen bg-[var(--paper)]">
      {/* Hero */}
      <div className="border-b border-[var(--border)]" style={{ background: "linear-gradient(135deg, var(--teal) 0%, #0A4A44 100%)" }}>
        <div className="max-w-4xl mx-auto px-6 py-20 text-center">
          <div className="inline-flex items-center gap-2 bg-white/10 text-white/90 text-xs font-semibold
                          uppercase tracking-widest rounded-full px-4 py-1.5 mb-6">
            Clinical Decision Support
          </div>
          <h1 className="font-display text-5xl font-bold text-white mb-4 leading-tight">
            MediAlert
          </h1>
          <p className="text-white/85 text-lg max-w-xl mx-auto mb-10 leading-relaxed">
            Instant, explainable 30-day diabetic readmission risk assessment for clinical
            staff in the Colombo district.
          </p>

          <div className="flex gap-4 justify-center">
            <button
              onClick={onGoToLogin}
              className="rounded-md bg-white text-[var(--teal)] font-semibold px-7 py-3
                         hover:bg-white/90 transition-colors shadow-sm"
            >
              Log in
            </button>
            <button
              onClick={onGoToRegister}
              className="rounded-md border-2 border-white/70 text-white font-semibold px-7 py-3
                         hover:bg-white/10 transition-colors"
            >
              Create an account
            </button>
          </div>
        </div>
      </div>

      {/* Feature grid */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="font-display text-2xl font-bold text-center text-[var(--ink)] mb-2">
          What this tool does
        </h2>

        <div className="grid sm:grid-cols-2 gap-5">
          <div className="bg-[var(--panel)] border border-[var(--border)] rounded-lg p-6">
            <div className="w-10 h-10 rounded-md bg-[var(--teal-soft)] text-[var(--teal)] flex items-center
                            justify-center font-bold text-lg mb-4">1</div>
            <h3 className="font-display font-semibold text-[var(--ink)] mb-2">Predicts risk</h3>
            <p className="text-sm text-[var(--ink-soft)] leading-relaxed">
              A statistically-validated machine learning model estimates 30-day readmission
              probability from routine clinical data.
            </p>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--border)] rounded-lg p-6">
            <div className="w-10 h-10 rounded-md bg-[var(--teal-soft)] text-[var(--teal)] flex items-center
                            justify-center font-bold text-lg mb-4">2</div>
            <h3 className="font-display font-semibold text-[var(--ink)] mb-2">Explains why</h3>
            <p className="text-sm text-[var(--ink-soft)] leading-relaxed">
              Every prediction comes with plain-language reasoning - not raw statistics a
              clinician has to decode.
            </p>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--border)] rounded-lg p-6">
            <div className="w-10 h-10 rounded-md bg-[var(--teal-soft)] text-[var(--teal)] flex items-center
                            justify-center font-bold text-lg mb-4">3</div>
            <h3 className="font-display font-semibold text-[var(--ink)] mb-2">Tracks history</h3>
            <p className="text-sm text-[var(--ink-soft)] leading-relaxed">
              Search a patient's past assessments and see how their predicted risk has changed
              over time.
            </p>
          </div>

          <div className="bg-[var(--panel)] border border-[var(--border)] rounded-lg p-6">
            <div className="w-10 h-10 rounded-md bg-[var(--teal-soft)] text-[var(--teal)] flex items-center
                            justify-center font-bold text-lg mb-4">4</div>
            <h3 className="font-display font-semibold text-[var(--ink)] mb-2">Documents it</h3>
            <p className="text-sm text-[var(--ink-soft)] leading-relaxed">
              Generate a downloadable PDF discharge summary directly from any completed
              assessment.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
