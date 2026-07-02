import { useState, type FormEvent } from 'react';
import { Navigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { useAuth } from '@/features/auth/AuthContext';
import { Button } from '@/components/Button';
import { TextInput } from '@/components/inputs/TextInput';
import { ApiError } from '@/services/apiClient';

const INSTITUTIONAL_DOMAIN = '@lazarza.com.mx';

export function LoginPage() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    // Validacion visual rapida; la validacion real vive en el backend
    if (!email.toLowerCase().trim().endsWith(INSTITUTIONAL_DOMAIN)) {
      setError(`El correo debe pertenecer al dominio ${INSTITUTIONAL_DOMAIN}`);
      return;
    }
    setIsSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo iniciar sesion');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <div className="w-full max-w-md rounded-card border border-border bg-surface p-8 shadow-soft">
        <div className="mb-8 flex flex-col items-center gap-3">
          <ShieldCheck className="h-10 w-10 text-primary" aria-hidden />
          <h1 className="text-subtitle text-textPrimary">DATA SENTINEL</h1>
          <p className="text-description text-textSecondary">Monitoreo de procesos ETL</p>
        </div>
        <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
          <TextInput
            id="login-email"
            label="Correo institucional"
            type="email"
            autoComplete="username"
            placeholder={`usuario${INSTITUTIONAL_DOMAIN}`}
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <TextInput
            id="login-password"
            label="Password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          {error && (
            <p className="rounded-control bg-danger/10 px-4 py-3 text-description text-danger" role="alert">
              {error}
            </p>
          )}
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Ingresando…' : 'Iniciar sesion'}
          </Button>
        </form>
      </div>
    </div>
  );
}
