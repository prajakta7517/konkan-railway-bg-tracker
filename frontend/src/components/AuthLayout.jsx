import { ShieldCheck } from "lucide-react";
import logo from "../assets/konkan-railway-logo.svg";

export default function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-navy-gradient p-10 text-white lg:flex">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "repeating-linear-gradient(135deg, #fff 0, #fff 1px, transparent 1px, transparent 18px)",
          }}
        />
        <div className="relative flex items-center gap-3">
          <img src={logo} alt="Konkan Railway" className="h-11 w-11 rounded-xl shadow-card" />
          <div className="leading-tight">
            <div className="font-semibold">Konkan Railway</div>
            <div className="text-xs text-navy-100">Corporation Limited</div>
          </div>
        </div>

        <div className="relative">
          <h1 className="mb-3 text-3xl font-bold leading-tight">
            Bank Guarantee
            <br />
            Tracking System
          </h1>
          <p className="max-w-sm text-sm leading-relaxed text-navy-100">
            A secure, internal register for tracking Bank Guarantee documents, expiry status,
            and automated renewal alerts across contractors and works.
          </p>
        </div>

        <div className="relative flex items-center gap-2 text-xs text-navy-100">
          <ShieldCheck className="h-4 w-4" />
          For authorized departmental use only.
        </div>
      </div>

      <div className="flex w-full flex-col items-center justify-center px-4 py-12 lg:w-1/2">
        <div className="mb-8 flex items-center gap-3 lg:hidden">
          <img src={logo} alt="Konkan Railway" className="h-10 w-10 rounded-xl shadow-card" />
          <div className="leading-tight">
            <div className="font-semibold text-navy-900">Konkan Railway</div>
            <div className="text-xs text-slate-500">Corporation Limited</div>
          </div>
        </div>

        <div className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-8 shadow-card">
          <h2 className="mb-1 text-center text-lg font-semibold text-navy-900">{title}</h2>
          {subtitle && <p className="mb-6 text-center text-sm text-slate-500">{subtitle}</p>}
          {children}
        </div>
      </div>
    </div>
  );
}
