# Crear usuarios — DATA SENTINEL

DATA SENTINEL **no tiene registro público**. El acceso está restringido a correos institucionales (`@lazarza.com.mx`) y cada usuario se crea manualmente con [scripts/create_user.py](../scripts/create_user.py).

---

## Requisito: configurar la conexión de administrador

El script necesita una credencial con permiso de escritura sobre `etl_execution_aws.app_users`. Se configura en `scripts/.env`:

```dotenv
DATABASE_ADMIN_URL=postgresql://usuario:password@host:5432/base_de_datos
AUTH_ALLOWED_EMAIL_DOMAIN=lazarza.com.mx
```

Si `scripts/.env` no existe o `DATABASE_ADMIN_URL` está vacía, el script **no falla** — en vez de ejecutar el `INSERT`, lo imprime en pantalla para que lo corras tú manualmente (psql, pgAdmin, DBeaver, etc.).

---

## Comando

Local (Windows/PowerShell):

```powershell
cd C:\Users\PracticanteBI\Documents\DataSentinel
.\apps\api\.venv\Scripts\python.exe scripts\create_user.py <correo> "<nombre completo>" [rol]
```

VPS (Linux):

```bash
cd /opt/datasentinel
sudo -u datasentinel apps/api/.venv/bin/python scripts/create_user.py <correo> "<nombre completo>" [rol]
```

### Ejemplo

```powershell
.\apps\api\.venv\Scripts\python.exe scripts\create_user.py becario.bi@lazarza.com.mx "Becario BI" admin
```

El script pide la contraseña dos veces por consola (no se ve mientras escribes — es normal):

```text
Password:
Confirmar password:
```

Mínimo 8 caracteres. Si coinciden y todo sale bien:

```text
Usuario becario.bi@lazarza.com.mx creado/actualizado (role=admin).
```

---

## Argumentos

| Posición | Nombre | Obligatorio | Descripción |
|---|---|---|---|
| 1 | correo | Sí | Debe terminar en `@lazarza.com.mx` (o el dominio configurado en `AUTH_ALLOWED_EMAIL_DOMAIN`). Se rechaza cualquier otro dominio |
| 2 | nombre completo | Sí | Entre comillas si tiene espacios |
| 3 | rol | No (default `viewer`) | `viewer` o `admin`. **Hoy ambos tienen los mismos permisos** — es solo una etiqueta descriptiva, no hay control de acceso diferenciado todavía |

---

## Comportamiento

- Es un **upsert**: si el correo ya existe, actualiza su contraseña, nombre y rol en vez de fallar. Útil también para "resetear" un usuario sin usar `change_password.py`.
- La contraseña se guarda con hash **bcrypt** — nunca en texto plano, nunca reversible.
- El usuario queda `is_active = TRUE` por defecto (puede iniciar sesión de inmediato).

---

## Verificar que se creó (opcional)

```sql
SELECT user_id, email, full_name, role, is_active, created_at
FROM etl_execution_aws.app_users
WHERE email = 'becario.bi@lazarza.com.mx';
```

---

## Desactivar un usuario

No hay comando para esto todavía — se hace directo en SQL:

```sql
UPDATE etl_execution_aws.app_users
SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
WHERE email = 'correo@lazarza.com.mx';
```

Un usuario inactivo no puede iniciar sesión aunque su contraseña sea correcta.

---

## Errores comunes

| Mensaje | Causa | Solución |
|---|---|---|
| `ForbiddenDomainError` / rechaza el correo | El correo no termina en `@lazarza.com.mx` | Usa un correo institucional |
| `DATABASE_ADMIN_URL no definida. Ejecuta manualmente:` | Falta configurar `scripts/.env` | Configúrala (ver arriba), o copia el SQL impreso y ejecútalo tú mismo |
| `Las contrasenas no coinciden` | Escribiste algo distinto en la confirmación | Vuelve a correr el script |
| Error de conexión a Postgres | Credenciales o red incorrectas en `DATABASE_ADMIN_URL` | Verifica host/usuario/password/puerto |

Relacionado: [CAMBIAR_CONTRASENA.md](CAMBIAR_CONTRASENA.md) — para cambiar la contraseña de un usuario que ya existe sin tocar su nombre/rol.
