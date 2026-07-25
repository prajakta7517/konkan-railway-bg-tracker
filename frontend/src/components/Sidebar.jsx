import { ClipboardList, History, LogOut, Users, X } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import logo from "../assets/konkan-railway-logo.svg";
import { useAuth } from "../context/AuthContext.jsx";

const navItems = [
  { to: "/dashboard", label: "BG Register", icon: ClipboardList, adminOnly: false },
  { to: "/users", label: "Users", icon: Users, adminOnly: true },
  { to: "/audit-log", label: "Audit Log", icon: History, adminOnly: true },
];

export default function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === "admin";

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const initials = (user?.full_name || "?")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-navy-gradient text-white transition-transform duration-200 lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between gap-3 border-b border-white/10 px-5 py-5">
          <div className="flex items-center gap-3">
            <img src={logo} alt="Konkan Railway" className="h-10 w-10 shrink-0 rounded-xl shadow-card" />
            <div className="leading-tight">
              <div className="text-sm font-semibold">Konkan Railway</div>
              <div className="text-[11px] text-navy-100">Corporation Limited</div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-navy-100 hover:bg-white/10 lg:hidden"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-5">
          {navItems
            .filter((item) => !item.adminOnly || isAdmin)
            .map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-white/10 text-white"
                      : "text-navy-100 hover:bg-white/5 hover:text-white"
                  }`
                }
              >
                <item.icon className="h-4 w-4" strokeWidth={2} />
                {item.label}
              </NavLink>
            ))}
        </nav>

        <div className="border-t border-white/10 px-4 py-4">
          <div className="mb-3 flex items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs font-semibold">
              {initials}
            </div>
            <div className="min-w-0 leading-tight">
              <div className="truncate text-sm font-medium">{user?.full_name}</div>
              <div className="text-[11px] capitalize text-navy-100">
                {user?.role === "admin" ? "Admin" : "Viewer / Data-Entry"}
              </div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-navy-100 transition-colors hover:bg-white/10 hover:text-white"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>
    </>
  );
}
