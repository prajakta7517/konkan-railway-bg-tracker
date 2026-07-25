import { History, Pencil, Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import api, { getErrorMessage } from "../api/client.js";

const ACTION_CONFIG = {
  create: { className: "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200", icon: Plus },
  update: { className: "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200", icon: Pencil },
  delete: { className: "bg-red-50 text-red-700 ring-1 ring-inset ring-red-200", icon: Trash2 },
};

function ActionBadge({ action }) {
  const config = ACTION_CONFIG[action] || {
    className: "bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200",
    icon: null,
  };
  const Icon = config.icon;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${config.className}`}>
      {Icon && <Icon className="h-3.5 w-3.5" strokeWidth={2.25} />}
      {action}
    </span>
  );
}

export default function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get("/audit-logs", { params: { page: 1, page_size: 100 } });
        setLogs(data.items);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-navy-900">Audit Log</h1>
        <p className="text-sm text-slate-500">Every create, edit, and delete on BG records, with who and when.</p>
      </div>

      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-card">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2.5">Timestamp</th>
              <th className="px-3 py-2.5">Action</th>
              <th className="px-3 py-2.5">Record ID</th>
              <th className="px-3 py-2.5">Changed By</th>
              <th className="px-3 py-2.5">Changes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={5} className="px-3 py-10 text-center text-slate-400">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && logs.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-12 text-center">
                  <div className="flex flex-col items-center gap-2 text-slate-400">
                    <History className="h-8 w-8" strokeWidth={1.5} />
                    <span>No audit entries yet.</span>
                  </div>
                </td>
              </tr>
            )}
            {!loading &&
              logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50">
                  <td className="whitespace-nowrap px-3 py-2.5">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-3 py-2.5">
                    <ActionBadge action={log.action} />
                  </td>
                  <td className="px-3 py-2.5 font-mono text-xs text-slate-500">{log.record_id}</td>
                  <td className="px-3 py-2.5">{log.changed_by_email}</td>
                  <td className="max-w-md truncate px-3 py-2.5 text-xs text-slate-500">
                    {JSON.stringify(log.changes)}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
