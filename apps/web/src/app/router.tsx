import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from '@/features/auth/AuthContext';
import { AppShell } from '@/components/layout/AppShell';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { ExecutionsPage } from '@/pages/ExecutionsPage';
import { ExecutionDetailPage } from '@/pages/ExecutionDetailPage';
import { HistoryPage } from '@/pages/HistoryPage';
import { StatisticsPage } from '@/pages/StatisticsPage';
import { AdminPage } from '@/pages/AdminPage';

function ProtectedLayout() {
  const { user, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <AppShell />;
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/executions" element={<ExecutionsPage />} />
        <Route path="/executions/:executionId" element={<ExecutionDetailPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/statistics" element={<StatisticsPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
