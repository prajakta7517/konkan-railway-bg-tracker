import { LogIn } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getErrorMessage } from "../api/client.js";
import AuthLayout from "../components/AuthLayout.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const HELPDESK_EMAIL = import.meta.env.VITE_HELPDESK_EMAIL || "helpdesk@konkanrailway.gov.in";
const HELPDESK_PHONE = import.meta.env.VITE_HELPDESK_PHONE || "+91-0000000000";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to the Bank Guarantee Tracking System">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            required
            autoComplete="username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-navy-600 focus:outline-none focus:ring-1 focus:ring-navy-600"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-navy-600 focus:outline-none focus:ring-1 focus:ring-navy-600"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="mt-2 flex items-center justify-center gap-2 rounded-md bg-navy-700 px-4 py-2 text-sm font-medium text-white hover:bg-navy-600 disabled:opacity-60"
        >
          <LogIn className="h-4 w-4" />
          {submitting ? "Signing in…" : "Login"}
        </button>
      </form>

      <div className="mt-4 text-center text-sm">
        <Link to="/forgot-password" className="text-navy-700 hover:underline">
          Forgot password?
        </Link>
      </div>

      <div className="mt-6 border-t border-slate-100 pt-4 text-center text-xs text-slate-500">
        <p className="font-medium text-slate-600">Need help accessing your account?</p>
        <p>
          Helpdesk: <a href={`mailto:${HELPDESK_EMAIL}`} className="hover:underline">{HELPDESK_EMAIL}</a>
        </p>
        <p>
          Phone: <a href={`tel:${HELPDESK_PHONE}`} className="hover:underline">{HELPDESK_PHONE}</a>
        </p>
      </div>
    </AuthLayout>
  );
}
