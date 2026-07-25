const TONES = {
  navy: "bg-navy-50 text-navy-700",
  emerald: "bg-emerald-50 text-emerald-700",
  amber: "bg-amber-50 text-amber-700",
  red: "bg-red-50 text-red-700",
};

export default function StatCard({ label, value, icon: Icon, tone = "navy", loading }) {
  return (
    <div className="flex items-center gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-card transition-shadow hover:shadow-card-hover">
      <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${TONES[tone]}`}>
        <Icon className="h-5 w-5" strokeWidth={2.25} />
      </div>
      <div className="min-w-0">
        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
        <div className="text-2xl font-semibold text-navy-900">{loading ? "—" : value}</div>
      </div>
    </div>
  );
}
