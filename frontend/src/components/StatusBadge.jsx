import { CircleAlert, CircleCheckBig, CircleX } from "lucide-react";

const CONFIG = {
  Active: {
    className: "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200",
    icon: CircleCheckBig,
  },
  "Expiring Soon": {
    className: "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200",
    icon: CircleAlert,
  },
  Expired: {
    className: "bg-red-50 text-red-700 ring-1 ring-inset ring-red-200",
    icon: CircleX,
  },
};

export default function StatusBadge({ status }) {
  const config = CONFIG[status] || {
    className: "bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200",
    icon: null,
  };
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${config.className}`}
    >
      {Icon && <Icon className="h-3.5 w-3.5" strokeWidth={2.25} />}
      {status}
    </span>
  );
}
