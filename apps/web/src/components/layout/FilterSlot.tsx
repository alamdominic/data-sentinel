/**
 * Permite que los filtros de cada pagina se muestren en la barra lateral
 * (escritorio) o en linea dentro de la pagina (movil/tablet).
 *
 * - En escritorio (lg+) el <PageFilters> se portea al hueco de la Sidebar,
 *   liberando espacio horizontal para el contenido.
 * - En movil la Sidebar vive detras del menu hamburguesa, asi que el filtro
 *   se renderiza en linea, donde siempre es visible.
 */
import {
  createContext,
  useContext,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from 'react';
import { createPortal } from 'react-dom';

/** Suscripcion a un media query sin flicker (SSR-safe). */
export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (onChange) => {
      const mql = window.matchMedia(query);
      mql.addEventListener('change', onChange);
      return () => mql.removeEventListener('change', onChange);
    },
    () => window.matchMedia(query).matches,
    () => false,
  );
}

/** Variante de maquetacion que consume FilterPanel para decidir si apila. */
export type FilterLayout = 'inline' | 'sidebar';
const FilterLayoutContext = createContext<FilterLayout>('inline');
export const useFilterLayout = () => useContext(FilterLayoutContext);

/** Registro del contenedor (hueco) dentro de la Sidebar de escritorio. */
interface FilterSlotContextValue {
  container: HTMLElement | null;
  setContainer: (el: HTMLElement | null) => void;
}
const FilterSlotContext = createContext<FilterSlotContextValue | null>(null);

export function FilterSlotProvider({ children }: { children: ReactNode }) {
  const [container, setContainer] = useState<HTMLElement | null>(null);
  return (
    <FilterSlotContext.Provider value={{ container, setContainer }}>
      {children}
    </FilterSlotContext.Provider>
  );
}

/** La Sidebar de escritorio usa esto para registrar su hueco de filtros. */
export function useRegisterFilterSlot() {
  const ctx = useContext(FilterSlotContext);
  return ctx?.setContainer ?? (() => {});
}

/**
 * Envuelve el filtro de una pagina. Decide entre portear a la Sidebar
 * (escritorio) o renderizar en linea (movil).
 */
export function PageFilters({ children }: { children: ReactNode }) {
  const ctx = useContext(FilterSlotContext);
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  if (isDesktop && ctx?.container) {
    return createPortal(
      <FilterLayoutContext.Provider value="sidebar">
        <div className="border-t border-border px-3 py-4">
          <p className="mb-3 px-1 text-label uppercase tracking-wide text-textMuted">Filtros</p>
          {children}
        </div>
      </FilterLayoutContext.Provider>,
      ctx.container,
    );
  }

  return <FilterLayoutContext.Provider value="inline">{children}</FilterLayoutContext.Provider>;
}
