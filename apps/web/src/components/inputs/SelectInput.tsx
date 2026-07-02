import type { SelectHTMLAttributes } from 'react';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectInputProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  placeholder?: string;
}

export function SelectInput({
  label,
  options,
  placeholder,
  id,
  className = '',
  ...rest
}: SelectInputProps) {
  return (
    <label className="flex flex-col gap-1.5" htmlFor={id}>
      {label && <span className="text-label text-textSecondary">{label}</span>}
      <select
        id={id}
        className={`h-12 rounded-control border border-border bg-surfaceElevated px-4 text-description text-textPrimary transition-colors focus:border-primary disabled:opacity-50 ${className}`}
        {...rest}
      >
        {placeholder !== undefined && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
