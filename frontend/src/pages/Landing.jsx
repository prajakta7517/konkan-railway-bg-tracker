import { Bell, FileStack, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import logo from "../assets/konkan-railway-logo.svg";

const features = [
  {
    icon: FileStack,
    title: "Centralized BG Register",
    description:
      "One authoritative record of every Bank Guarantee — number, work, contractor, dates, and supporting documents.",
  },
  {
    icon: Bell,
    title: "Automated Expiry Alerts",
    description:
      "Countdown email reminders in the seven days before a guarantee expires, so renewals never slip through.",
  },
  {
    icon: ShieldCheck,
    title: "Full Audit Trail",
    description:
      "Every create, edit, and deletion is logged with who, what, and when — records are never silently lost.",
  },
];

export default function Landing() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <div className="relative overflow-hidden bg-navy-gradient text-white">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "repeating-linear-gradient(135deg, #fff 0, #fff 1px, transparent 1px, transparent 18px)",
          }}
        />
        <header className="relative mx-auto max-w-6xl px-6 py-5 sm:px-8">
          <div className="flex items-center gap-3">
            <img src={logo} alt="Konkan Railway" className="h-10 w-10 rounded-xl shadow-card" />
            <span className="text-lg font-semibold">Konkan Railway Corporation Limited</span>
          </div>
        </header>

        <main className="relative mx-auto flex max-w-3xl flex-col items-start gap-6 px-6 py-20 sm:px-8">
          <h1 className="text-3xl font-bold leading-tight sm:text-4xl">
            Bank Guarantee Tracking System
          </h1>
          <p className="text-base leading-relaxed text-navy-100">
            A secure, internal register for tracking Bank Guarantee documents submitted by
            contractors, with automated expiry alerts. This system maintains a central record of
            BG numbers, issue and expiry dates, associated work, and responsible personnel — and
            sends countdown email reminders in the seven days before a guarantee expires.
          </p>
          <Link
            to="/login"
            className="rounded-md bg-gold-gradient px-6 py-2.5 font-medium text-navy-900 shadow-card hover:brightness-105"
          >
            Login
          </Link>
        </main>
      </div>

      <section className="mx-auto grid w-full max-w-6xl grid-cols-1 gap-6 px-6 py-14 sm:px-8 md:grid-cols-3">
        {features.map((f) => (
          <div key={f.title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-card">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-navy-50 text-navy-700">
              <f.icon className="h-5 w-5" strokeWidth={2.25} />
            </div>
            <h3 className="mb-1 text-sm font-semibold text-navy-900">{f.title}</h3>
            <p className="text-sm leading-relaxed text-slate-600">{f.description}</p>
          </div>
        ))}
      </section>

      <footer className="mt-auto border-t border-slate-200 px-6 py-4 text-center text-xs text-slate-400">
        For authorized departmental use only. Unauthorized access is prohibited.
      </footer>
    </div>
  );
}
