import type { InputHTMLAttributes } from 'react';

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function TextInput({ label, error, id, className = '', ...rest }: TextInputProps) {
  return (
    <label className="flex flex-col gap-1.5" htmlFor={id}>
      {label && <span className="text-label text-textSecondary">{label}</span>}
      <input
        id={id}
        className={`h-12 rounded-control border bg-surfaceElevated px-4 text-description text-textPrimary placeholder:text-textMuted transition-colors focus:border-primary disabled:opacity-50 ${
          error ? 'border-danger' : 'border-border'
        } ${className}`}
        {...rest}
      />
      {error && <span className="text-label text-danger">{error}</span>}
    </label>
  );
}
