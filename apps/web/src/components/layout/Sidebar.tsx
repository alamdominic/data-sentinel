import { NavLink } from 'react-router-dom';
import {
  Activity,
  BarChart3,
  History,
  LayoutDashboard,
  LogOut,
  Settings2,
  ShieldCheck,
  UserRound,
} from 'lucide-react';
import { useAuth } from '@/features/auth/AuthContext';
import { useRegisterFilterSlot } from '@/components/layout/FilterSlot';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/executions', label: 'Ejecuciones', icon: Activity, end: false },
  { to: '/history', label: 'Historial', icon: History, end: false },
  { to: '/statistics', label: 'Estadisticas', icon: BarChart3, end: false },
  { to: '/admin', label: 'Administracion', icon: Settings2, end: false },
];

export function Sidebar({
  onNavigate,
  showFilterSlot = false,
}: {
  onNavigate?: () => void;
  showFilterSlot?: boolean;
}) {
  const { user, logout } = useAuth();
  const registerFilterSlot = useRegisterFilterSlot();

  return (
    <aside className="flex h-full w-[260px] flex-col border-r border-border bg-surface">
      <div className="flex items-center gap-2 px-6 py-6">
        <ShieldCheck className="h-6 w-6 text-primary" aria-hidden />
        <span className="text-heading font-semibold tracking-tight text-textPrimary">
          DATA SENTINEL
        </span>
      </div>
      <div className="flex flex-1 flex-col overflow-y-auto">
        <nav className="flex flex-col gap-1 px-3" aria-label="Navegacion principal">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onNavigate}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-control px-3 py-2.5 text-description transition-colors ${
                  isActive
                    ? 'bg-primary/15 font-medium text-primary'
                    : 'text-textSecondary hover:bg-surfaceElevated hover:text-textPrimary'
                }`
              }
            >
              <Icon className="h-5 w-5" aria-hidden />
              {label}
            </NavLink>
          ))}
        </nav>
        {/* Hueco donde las paginas portean sus filtros en escritorio. */}
        {showFilterSlot && <div ref={registerFilterSlot} className="mt-2" />}
      </div>
      <div className="border-t border-border px-3 py-4">
        <div className="flex items-center gap-3 rounded-control px-3 py-2">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/15 text-primary">
            <UserRound className="h-5 w-5" aria-hidden />
          </div>
          <div className="min-w-0">
            <p className="truncate text-description text-textPrimary">
              {user?.fullName ?? user?.email}
            </p>
            <p className="truncate text-label text-textMuted">{user?.role}</p>
          </div>
        </div>
        <button
          className="mt-1 flex w-full items-center gap-3 rounded-control px-3 py-2.5 text-description text-textSecondary transition-colors hover:bg-surfaceElevated hover:text-textPrimary"
          onClick={logout}
        >
          <LogOut className="h-5 w-5" aria-hidden />
          Salir
        </button>
        <p className="px-3 pt-3 text-label text-textMuted">Monitoreo ETL · v1.0</p>
      </div>
    </aside>
  );
}
