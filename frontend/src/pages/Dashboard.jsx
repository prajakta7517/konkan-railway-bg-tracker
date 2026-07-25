import {
  CircleAlert,
  CircleCheckBig,
  CircleX,
  FileStack,
  Paperclip,
  Plus,
  Search,
  SquarePen,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import api, { getErrorMessage } from "../api/client.js";
import BGFormModal from "../components/BGFormModal.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import StatCard from "../components/StatCard.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const PAGE_SIZE = 25;
const emptyStats = { total: null, active: null, expiringSoon: null, expired: null };

export default function Dashboard() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortDir, setSortDir] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [stats, setStats] = useState(emptyStats);

  const [showForm, setShowForm] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [deletingRecord, setDeletingRecord] = useState(null);

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get("/bg-records", {
        params: {
          search: search || undefined,
          status: statusFilter || undefined,
          sort_by: "expiry_date",
          sort_dir: sortDir,
          page,
          page_size: PAGE_SIZE,
        },
      });
      setRecords(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, sortDir, page]);

  const fetchStats = useCallback(async () => {
    try {
      const [all, active, expiringSoon, expired] = await Promise.all([
        api.get("/bg-records", { params: { page: 1, page_size: 1 } }),
        api.get("/bg-records", { params: { status: "Active", page: 1, page_size: 1 } }),
        api.get("/bg-records", { params: { status: "Expiring Soon", page: 1, page_size: 1 } }),
        api.get("/bg-records", { params: { status: "Expired", page: 1, page_size: 1 } }),
      ]);
      setStats({
        total: all.data.total,
        active: active.data.total,
        expiringSoon: expiringSoon.data.total,
        expired: expired.data.total,
      });
    } catch {
      // Stat cards are a non-critical summary; silently leave placeholders on failure.
    }
  }, []);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const refreshAll = () => {
    fetchRecords();
    fetchStats();
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchRecords();
  };

  const handleDelete = async () => {
    try {
      await api.delete(`/bg-records/${deletingRecord.id}`);
      setDeletingRecord(null);
      refreshAll();
    } catch (err) {
      setError(getErrorMessage(err));
      setDeletingRecord(null);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-navy-900">Bank Guarantee Register</h1>
          <p className="text-sm text-slate-500">
            Track BG documents, expiry status, and renewal alerts.
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-1.5 rounded-md bg-navy-700 px-4 py-2 text-sm font-medium text-white shadow-card hover:bg-navy-600"
        >
          <Plus className="h-4 w-4" />
          Add BG Record
        </button>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Records" value={stats.total} icon={FileStack} tone="navy" loading={stats.total === null} />
        <StatCard label="Active" value={stats.active} icon={CircleCheckBig} tone="emerald" loading={stats.active === null} />
        <StatCard label="Expiring Soon" value={stats.expiringSoon} icon={CircleAlert} tone="amber" loading={stats.expiringSoon === null} />
        <StatCard label="Expired" value={stats.expired} icon={CircleX} tone="red" loading={stats.expired === null} />
      </div>

      <form onSubmit={handleSearchSubmit} className="mb-4 flex flex-wrap gap-3">
        <div className="relative w-full max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by BG number, contractor, or work name…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-md border border-slate-300 py-2 pl-9 pr-3 text-sm focus:border-navy-600 focus:outline-none focus:ring-1 focus:ring-navy-600"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-navy-600 focus:outline-none focus:ring-1 focus:ring-navy-600"
        >
          <option value="">All statuses</option>
          <option value="Active">Active</option>
          <option value="Expiring Soon">Expiring Soon</option>
          <option value="Expired">Expired</option>
        </select>
        <select
          value={sortDir}
          onChange={(e) => setSortDir(Number(e.target.value))}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-navy-600 focus:outline-none focus:ring-1 focus:ring-navy-600"
        >
          <option value={1}>Expiry: Soonest first</option>
          <option value={-1}>Expiry: Latest first</option>
        </select>
        <button
          type="submit"
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Search
        </button>
      </form>

      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-card">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2.5">Sr.</th>
              <th className="px-3 py-2.5">BG Number</th>
              <th className="px-3 py-2.5">Name of Work</th>
              <th className="px-3 py-2.5">Contractor</th>
              <th className="px-3 py-2.5">Issue Date</th>
              <th className="px-3 py-2.5">Expiry Date</th>
              <th className="px-3 py-2.5">Assigned To</th>
              <th className="px-3 py-2.5">Contact</th>
              <th className="px-3 py-2.5">Document</th>
              <th className="px-3 py-2.5">Status</th>
              <th className="px-3 py-2.5">Remarks</th>
              {isAdmin && <th className="px-3 py-2.5">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={12} className="px-3 py-10 text-center text-slate-400">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && records.length === 0 && (
              <tr>
                <td colSpan={12} className="px-3 py-12 text-center">
                  <div className="flex flex-col items-center gap-2 text-slate-400">
                    <FileStack className="h-8 w-8" strokeWidth={1.5} />
                    <span>No records found.</span>
                  </div>
                </td>
              </tr>
            )}
            {!loading &&
              records.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50">
                  <td className="px-3 py-2.5 text-slate-500">{r.sr_no}</td>
                  <td className="px-3 py-2.5 font-medium text-navy-800">{r.bg_number}</td>
                  <td className="px-3 py-2.5">{r.name_of_work}</td>
                  <td className="px-3 py-2.5">{r.contractor_name}</td>
                  <td className="px-3 py-2.5 whitespace-nowrap">{r.issue_date}</td>
                  <td className="px-3 py-2.5 whitespace-nowrap">{r.expiry_date}</td>
                  <td className="px-3 py-2.5">{r.assigned_to}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-500">
                    <div>{r.mobile_no}</div>
                    <div>{r.email}</div>
                  </td>
                  <td className="px-3 py-2.5">
                    {r.document_url ? (
                      <a
                        href={r.document_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-navy-700 hover:underline"
                      >
                        <Paperclip className="h-3.5 w-3.5" />
                        View
                      </a>
                    ) : (
                      <span className="text-slate-300">—</span>
                    )}
                  </td>
                  <td className="px-3 py-2.5">
                    <StatusBadge status={r.status} />
                  </td>
                  <td className="max-w-xs truncate px-3 py-2.5 text-slate-500">{r.remarks}</td>
                  {isAdmin && (
                    <td className="whitespace-nowrap px-3 py-2.5">
                      <button
                        onClick={() => setEditingRecord(r)}
                        title="Edit"
                        className="mr-2 inline-flex items-center rounded p-1.5 text-navy-700 hover:bg-navy-50"
                      >
                        <SquarePen className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setDeletingRecord(r)}
                        title="Delete"
                        className="inline-flex items-center rounded p-1.5 text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  )}
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
        <span>
          {total} record{total !== 1 ? "s" : ""}
        </span>
        <div className="flex gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 disabled:opacity-40"
          >
            Previous
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>

      {showForm && (
        <BGFormModal
          onClose={() => setShowForm(false)}
          onSaved={() => {
            setShowForm(false);
            refreshAll();
          }}
        />
      )}

      {editingRecord && (
        <BGFormModal
          record={editingRecord}
          onClose={() => setEditingRecord(null)}
          onSaved={() => {
            setEditingRecord(null);
            refreshAll();
          }}
        />
      )}

      {deletingRecord && (
        <ConfirmDialog
          title="Delete BG Record"
          message={`Are you sure you want to delete BG ${deletingRecord.bg_number}? This record will be removed from the active register but retained for audit purposes.`}
          confirmLabel="Delete"
          danger
          onConfirm={handleDelete}
          onCancel={() => setDeletingRecord(null)}
        />
      )}
    </div>
  );
}
