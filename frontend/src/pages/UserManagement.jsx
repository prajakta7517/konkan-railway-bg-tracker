import { Trash2, UserPlus, Users as UsersIcon } from "lucide-react";
import { useEffect, useState } from "react";
import api, { getErrorMessage } from "../api/client.js";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const emptyForm = { email: "", password: "", full_name: "", role: "viewer" };

function initialsOf(name) {
  return (name || "?")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export default function UserManagement() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deletingUser, setDeletingUser] = useState(null);

  const fetchUsers = async () => {
    try {
      const { data } = await api.get("/users");
      setUsers(data);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleChange = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");
    setSubmitting(true);
    try {
      await api.post("/users", form);
      setForm(emptyForm);
      setMessage("User created.");
      fetchUsers();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const toggleActive = async (u) => {
    try {
      await api.patch(`/users/${u.id}/active`, { is_active: !u.is_active });
      fetchUsers();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const changeRole = async (u, role) => {
    try {
      await api.patch(`/users/${u.id}/role`, { role });
      fetchUsers();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleDelete = async () => {
    try {
      await api.delete(`/users/${deletingUser.id}`);
      setDeletingUser(null);
      fetchUsers();
    } catch (err) {
      setError(getErrorMessage(err));
      setDeletingUser(null);
    }
  };

  const inputClass =
    "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-navy-600 focus:outline-none focus:ring-1 focus:ring-navy-600";

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-navy-900">User Management</h1>
        <p className="text-sm text-slate-500">Manage who can access the BG register and their role.</p>
      </div>

      <div className="mb-8 rounded-lg border border-slate-200 bg-white p-4 shadow-card">
        <div className="mb-3 flex items-center gap-2 text-sm font-medium text-navy-800">
          <UserPlus className="h-4 w-4" />
          Add a user
        </div>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-3 sm:grid-cols-5">
          <input
            required
            placeholder="Full name"
            className={inputClass}
            value={form.full_name}
            onChange={handleChange("full_name")}
          />
          <input
            required
            type="email"
            placeholder="Email"
            className={inputClass}
            value={form.email}
            onChange={handleChange("email")}
          />
          <input
            required
            type="password"
            minLength={8}
            placeholder="Temporary password"
            className={inputClass}
            value={form.password}
            onChange={handleChange("password")}
          />
          <select className={inputClass} value={form.role} onChange={handleChange("role")}>
            <option value="viewer">Viewer / Data-Entry</option>
            <option value="admin">Admin</option>
          </select>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-navy-700 px-4 py-2 text-sm font-medium text-white hover:bg-navy-600 disabled:opacity-60"
          >
            {submitting ? "Adding…" : "Add User"}
          </button>
        </form>
      </div>

      {message && <p className="mb-3 text-sm text-emerald-700">{message}</p>}
      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-card">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2.5">Name</th>
              <th className="px-3 py-2.5">Email</th>
              <th className="px-3 py-2.5">Role</th>
              <th className="px-3 py-2.5">Status</th>
              <th className="px-3 py-2.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {users.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-10 text-center">
                  <div className="flex flex-col items-center gap-2 text-slate-400">
                    <UsersIcon className="h-8 w-8" strokeWidth={1.5} />
                    <span>No users yet.</span>
                  </div>
                </td>
              </tr>
            )}
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-slate-50">
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-navy-50 text-xs font-semibold text-navy-700">
                      {initialsOf(u.full_name)}
                    </div>
                    {u.full_name}
                  </div>
                </td>
                <td className="px-3 py-2.5">{u.email}</td>
                <td className="px-3 py-2.5">
                  <select
                    value={u.role}
                    onChange={(e) => changeRole(u, e.target.value)}
                    className="rounded border border-slate-300 px-2 py-1 text-xs"
                  >
                    <option value="viewer">Viewer / Data-Entry</option>
                    <option value="admin">Admin</option>
                  </select>
                </td>
                <td className="px-3 py-2.5">
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      u.is_active
                        ? "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200"
                        : "bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200"
                    }`}
                  >
                    {u.is_active ? "Active" : "Disabled"}
                  </span>
                </td>
                <td className="px-3 py-2.5">
                  <button
                    onClick={() => toggleActive(u)}
                    className="mr-3 text-navy-700 hover:underline"
                  >
                    {u.is_active ? "Disable" : "Enable"}
                  </button>
                  {u.id !== currentUser?.id && (
                    <button
                      onClick={() => setDeletingUser(u)}
                      title="Delete user"
                      className="inline-flex items-center text-red-600 hover:underline"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {deletingUser && (
        <ConfirmDialog
          title="Delete User"
          message={`Are you sure you want to delete ${deletingUser.full_name} (${deletingUser.email})? This cannot be undone.`}
          confirmLabel="Delete"
          danger
          onConfirm={handleDelete}
          onCancel={() => setDeletingUser(null)}
        />
      )}
    </div>
  );
}
