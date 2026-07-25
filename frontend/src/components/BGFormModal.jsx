import { Plus, SquarePen } from "lucide-react";
import { useState } from "react";
import api, { getErrorMessage } from "../api/client.js";

const emptyForm = {
  bg_number: "",
  name_of_work: "",
  contractor_name: "",
  issue_date: "",
  expiry_date: "",
  remarks: "",
  assigned_to: "",
  mobile_no: "",
  email: "",
};

export default function BGFormModal({ record, onClose, onSaved }) {
  const isEdit = Boolean(record);
  const [form, setForm] = useState(
    isEdit
      ? {
          bg_number: record.bg_number,
          name_of_work: record.name_of_work,
          contractor_name: record.contractor_name,
          issue_date: record.issue_date,
          expiry_date: record.expiry_date,
          remarks: record.remarks || "",
          assigned_to: record.assigned_to,
          mobile_no: record.mobile_no,
          email: record.email,
        }
      : emptyForm
  );
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    const formData = new FormData();
    Object.entries(form).forEach(([key, value]) => formData.append(key, value));
    if (file) formData.append("file", file);

    try {
      if (isEdit) {
        await api.patch(`/bg-records/${record.id}`, formData);
      } else {
        await api.post("/bg-records", formData);
      }
      onSaved();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const inputClass =
    "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-navy-600 focus:outline-none focus:ring-1 focus:ring-navy-600";
  const labelClass = "mb-1 block text-sm font-medium text-slate-700";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/40 px-4 py-8">
      <div className="w-full max-w-2xl rounded-lg bg-white p-6 shadow-xl">
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-navy-50 text-navy-700">
            {isEdit ? <SquarePen className="h-5 w-5" strokeWidth={2.25} /> : <Plus className="h-5 w-5" strokeWidth={2.25} />}
          </div>
          <h2 className="text-base font-semibold text-navy-900">
            {isEdit ? "Edit Bank Guarantee Record" : "Add Bank Guarantee Record"}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className={labelClass}>Bank Guarantee Number</label>
            <input required className={inputClass} value={form.bg_number} onChange={handleChange("bg_number")} />
          </div>
          <div>
            <label className={labelClass}>Contractor Name</label>
            <input required className={inputClass} value={form.contractor_name} onChange={handleChange("contractor_name")} />
          </div>

          <div className="sm:col-span-2">
            <label className={labelClass}>Name of Work</label>
            <input required className={inputClass} value={form.name_of_work} onChange={handleChange("name_of_work")} />
          </div>

          <div>
            <label className={labelClass}>Issue Date</label>
            <input required type="date" className={inputClass} value={form.issue_date} onChange={handleChange("issue_date")} />
          </div>
          <div>
            <label className={labelClass}>Expiry Date</label>
            <input required type="date" className={inputClass} value={form.expiry_date} onChange={handleChange("expiry_date")} />
          </div>

          <div>
            <label className={labelClass}>Assigned To</label>
            <input required className={inputClass} value={form.assigned_to} onChange={handleChange("assigned_to")} />
          </div>
          <div>
            <label className={labelClass}>Mobile No.</label>
            <input required className={inputClass} value={form.mobile_no} onChange={handleChange("mobile_no")} />
          </div>

          <div>
            <label className={labelClass}>Email (for alerts)</label>
            <input required type="email" className={inputClass} value={form.email} onChange={handleChange("email")} />
          </div>
          <div>
            <label className={labelClass}>
              Document {isEdit && <span className="text-xs text-slate-400">(leave blank to keep existing)</span>}
            </label>
            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.docx"
              className={inputClass}
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>

          <div className="sm:col-span-2">
            <label className={labelClass}>Remarks</label>
            <textarea className={inputClass} rows={2} value={form.remarks} onChange={handleChange("remarks")} />
          </div>

          {error && <p className="sm:col-span-2 text-sm text-red-600">{error}</p>}

          <div className="flex justify-end gap-3 sm:col-span-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-md bg-navy-700 px-4 py-2 text-sm font-medium text-white hover:bg-navy-600 disabled:opacity-60"
            >
              {submitting ? "Saving…" : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
