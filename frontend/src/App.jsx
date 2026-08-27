import { useEffect, useState } from "react";
import AssessmentForm from "./components/AssessmentForm";
import RiskResult from "./components/RiskResult";
import HistoryView from "./components/HistoryView";
import DashboardView from "./components/DashboardView";
import ProfileView from "./components/ProfileView";
import HomePage from "./components/HomePage";
import LoginPage from "./components/LoginPage";
import RegisterPage from "./components/RegisterPage";
import { fetchFormOptions, submitAssessment, isLoggedIn, logoutUser } from "./api/predictClient";

const TABS = [
  { id: "assess", label: "New Assessment" },
  { id: "history", label: "Patient History" },
  { id: "dashboard", label: "Dashboard" },
];

export default function App() {

  const [publicView, setPublicView] = useState("home");
  const [authed, setAuthed] = useState(isLoggedIn());

  const [activeTab, setActiveTab] = useState("assess");
  const [formOptions, setFormOptions] = useState(null);
  const [optionsError, setOptionsError] = useState(null);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [sessionMessage, setSessionMessage] = useState(null);

  useEffect(() => {
    if (!authed) return;
    fetchFormOptions()
      .then(setFormOptions)
      .catch((err) => setOptionsError(err.message));
  }, [authed]);

  const handleSessionExpired = () => {
    setAuthed(false);
    setPublicView("login");
    setSessionMessage("Your session expired. Please log in again.");
    setResult(null);
    setFormOptions(null);
  };

  const handleSubmit = async (payload) => {
    setSubmitting(true);
    setSubmitError(null);
    try {
      const prediction = await submitAssessment(payload);
      setResult(prediction);
    } catch (err) {
      if (err.name === "SessionExpiredError") {
        handleSessionExpired();
      } else {
        setSubmitError(err.message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const goToNewAssessment = () => {
    setResult(null);
    setActiveTab("assess");
  };

  const handleLogout = () => {
    logoutUser();
    setAuthed(false);
    setPublicView("home");
    setResult(null);
    setFormOptions(null);
  };

  const handleLoginSuccess = () => {
    setAuthed(true);
    setSessionMessage(null);
  };

  // Logged-out flow: Home / Login / Register

  if (!authed) {
    if (publicView === "login") {
      return (
        <>
          {sessionMessage && (
            <div className="max-w-sm mx-auto mt-4 rounded-md border border-[var(--risk-medium)] bg-[var(--risk-medium-bg)] p-3 text-sm text-center">
              {sessionMessage}
            </div>
          )}
          <LoginPage
            onLoginSuccess={handleLoginSuccess}
            onGoToRegister={() => setPublicView("register")}
            onGoHome={() => setPublicView("home")}
          />
        </>
      );
    }
    if (publicView === "register") {
      return (
        <RegisterPage
          onRegisterSuccess={() => {
            setSessionMessage("Account created. Please log in.");
            setPublicView("login");
          }}
          onGoToLogin={() => setPublicView("login")}
          onGoHome={() => setPublicView("home")}
        />
      );
    }
    return (
      <HomePage
        onGoToLogin={() => setPublicView("login")}
        onGoToRegister={() => setPublicView("register")}
      />
    );
  }

  // Authenticated app

  return (
    <div className="min-h-screen bg-[var(--paper)]">
      <header className="border-b border-[var(--border)] bg-[var(--panel)]">
        <div className="max-w-3xl mx-auto px-6 py-6 flex items-start justify-between">
          <div>
            <h1 className="font-display text-2xl">MediAlert</h1>
            <p className="text-sm text-[var(--ink-soft)] mt-1">
              30-day diabetic readmission risk assessment · Colombo district clinical decision support
            </p>
          </div>
          <div className="flex items-center gap-3 mt-1">
            <button
              onClick={() => setActiveTab("profile")}
              className="text-sm text-[var(--ink-soft)] hover:text-[var(--teal)] transition-colors"
            >
              Profile
            </button>
            <button
              onClick={handleLogout}
              className="text-sm rounded-md border border-[var(--border)] text-[var(--ink)] font-medium
                         px-4 py-1.5 hover:bg-[var(--paper)] hover:border-[var(--ink-soft)] transition-colors"
            >
              Log out
            </button>
          </div>
        </div>
        <nav className="max-w-3xl mx-auto px-6 flex gap-6 -mb-px">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                if (tab.id === "assess") setResult(null);
              }}
              className={`text-sm py-3 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-[var(--teal)] text-[var(--teal)] font-medium"
                  : "border-transparent text-[var(--ink-soft)] hover:text-[var(--ink)]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-10">
        {optionsError && (
          <div className="rounded-md border border-[var(--risk-high)] bg-[var(--risk-high-bg)] p-4 mb-6 text-sm">
            <strong>Cannot reach the prediction service.</strong> {optionsError}
            <div className="mt-1 text-[var(--ink-soft)]">
              Confirm the API is running: <code className="font-mono">uvicorn backend.main:app --reload</code>
            </div>
          </div>
        )}

        {activeTab === "assess" && (
          <>
            {submitError && (
              <div className="rounded-md border border-[var(--risk-high)] bg-[var(--risk-high-bg)] p-4 mb-6 text-sm">
                <strong>Could not complete assessment.</strong> {submitError}
              </div>
            )}

            {!formOptions && !optionsError && (
              <p className="text-sm text-[var(--ink-soft)]">Loading form...</p>
            )}

            {formOptions && !result && (
              <AssessmentForm
                formOptions={formOptions}
                onSubmit={handleSubmit}
                submitting={submitting}
              />
            )}

            {result && (
              <RiskResult result={result} onReset={goToNewAssessment} onSessionExpired={handleSessionExpired} />
            )}
          </>
        )}

        {activeTab === "history" && <HistoryView onSessionExpired={handleSessionExpired} />}
        {activeTab === "dashboard" && <DashboardView onSessionExpired={handleSessionExpired} />}
        {activeTab === "profile" && <ProfileView onSessionExpired={handleSessionExpired} />}
      </main>
    </div>
  );
}
