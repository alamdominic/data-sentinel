import { useState } from 'react';
import { Menu } from 'lucide-react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { FilterSlotProvider } from '@/components/layout/FilterSlot';

export function AppShell() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <FilterSlotProvider>
    <div className="flex min-h-screen bg-background">
      <div className="sticky top-0 hidden h-screen self-start lg:block">
        <Sidebar showFilterSlot />
      </div>
      {isSidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setIsSidebarOpen(false)}
            aria-hidden
          />
          <div className="absolute inset-y-0 left-0 z-50">
            <Sidebar onNavigate={() => setIsSidebarOpen(false)} />
          </div>
        </div>
      )}
      <div className="flex min-w-0 flex-1 flex-col">
        <button
          className="fixed left-4 top-4 z-30 rounded-control bg-surface p-2 text-textSecondary shadow-sm transition-colors hover:bg-surfaceElevated lg:hidden"
          onClick={() => setIsSidebarOpen((open) => !open)}
          aria-label="Abrir navegacion"
        >
          <Menu className="h-5 w-5" />
        </button>
        <main className="mx-auto w-full max-w-layout flex-1 p-4 pt-16 sm:p-6 sm:pt-16 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
    </FilterSlotProvider>
  );
}
