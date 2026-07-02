# Cambiar contraseña — DATA SENTINEL

La aplicación web **no permite cambiar contraseñas** (por diseño — ver [SPEC.md](../steps/SPEC.md)). Todo cambio lo hace el ingeniero de datos en local o en el servidor con [scripts/change_password.py](../scripts/change_password.py).

---

## Por qué no se puede "recuperar" una contraseña

Las contraseñas se guardan con **hash bcrypt** — es un algoritmo de una sola vía. No existe variable de entorno, llave ni comando que "descifre" un hash para devolver la contraseña original; es matemáticamente imposible por diseño, y es lo correcto: si la base de datos se filtra, ninguna contraseña queda expuesta.

Lo que sí existe es **resetear**: asignar una contraseña nueva. Eso es lo que hace este script.

---

## Requisito: configurar la conexión de administrador

Igual que para crear usuarios, en `scripts/.env`:

```dotenv
DATABASE_ADMIN_URL=postgresql://usuario:password@host:5432/base_de_datos
AUTH_ALLOWED_EMAIL_DOMAIN=lazarza.com.mx
```

Sin esto configurado, el script imprime el `UPDATE` en pantalla para ejecutarlo tú manualmente en vez de fallar.

---

## Modo 1 — Elegir la nueva contraseña

Local (PowerShell):

```powershell
cd C:\Users\PracticanteBI\Documents\DataSentinel
.\apps\api\.venv\Scripts\python.exe scripts\change_password.py becario.bi@lazarza.com.mx
```

VPS (Linux):

```bash
cd /opt/datasentinel
sudo -u datasentinel apps/api/.venv/bin/python scripts/change_password.py becario.bi@lazarza.com.mx
```

Pide la contraseña dos veces (mínimo 8 caracteres, no se ve mientras escribes):

```text
Nueva contrasena:
Confirmar contrasena:
```

Al terminar:

```text
Contrasena actualizada para becario.bi@lazarza.com.mx.
```

---

## Modo 2 — Generar una contraseña aleatoria

Útil cuando quieres entregarle algo temporal al usuario sin decidir tú el valor:

```powershell
.\apps\api\.venv\Scripts\python.exe scripts\change_password.py becario.bi@lazarza.com.mx --generate
```

Salida:

```text
Contrasena actualizada para becario.bi@lazarza.com.mx.

Contrasena generada (entregala por canal seguro; no se puede recuperar despues):
RC0rKnQJQ7OGf-VS
```

**Se muestra una sola vez.** Si la pierdes, no hay forma de recuperarla — vuelve a correr el comando para generar otra.

---

## Entrega segura al usuario

- No la mandes por correo sin cifrar ni la dejes en un chat sin borrar después.
- Prioriza un canal ya validado (llamada, mensaje directo que se pueda borrar, gestor de contraseñas compartido).
- Sugiere al usuario que la use tal cual (son aleatorias y seguras) — no hay forma de cambiarla desde la web después, así que si prefiere una memorizable, usa el Modo 1 con la contraseña que él elija en vivo contigo.

---

## Errores comunes

| Mensaje | Causa | Solución |
|---|---|---|
| `No existe usuario con correo ...` | El correo no está registrado | Créalo primero con [CREAR_USUARIOS.md](CREAR_USUARIOS.md) |
| Rechaza el correo por dominio | No termina en `@lazarza.com.mx` | Usa el correo institucional correcto |
| `Las contrasenas no coinciden` | Typo en la confirmación (Modo 1) | Vuelve a correr el comando |
| `DATABASE_ADMIN_URL no definida...` | Falta `scripts/.env` | Configúrala, o ejecuta el SQL impreso manualmente |

Relacionado: [CREAR_USUARIOS.md](CREAR_USUARIOS.md).
