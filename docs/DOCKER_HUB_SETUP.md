# Conectar Docker Hub a tu computadora

Paso previo a [DEPLOY_VPS.md](DEPLOY_VPS.md): necesitas una cuenta de Docker Hub y tu máquina autenticada contra ella antes de poder hacer `docker compose push`.

---

## ¿Ya estás logueado?

Antes de crear cuenta o token, revisa si tu máquina ya tiene sesión:

**Windows (PowerShell)** — no tiene `grep`, usa `Select-String`:

```powershell
docker info | Select-String Username
```

**Linux/Mac (bash)**:

```bash
docker info | grep Username
```

- Si muestra `Username: tu_usuario` → ya estás logueado, pasa directo al [Paso 4](#paso-4--configurar-tu-usuario-en-el-proyecto) (configurar `DOCKERHUB_USER`).
- Si no muestra nada → no hay sesión activa, sigue con el Paso 1.

Alternativa (revisa el archivo de credenciales directo, sin depender de `docker info`):

```powershell
# Windows
type $env:USERPROFILE\.docker\config.json
```

```bash
# Linux/Mac
cat ~/.docker/config.json
```

Si existe una clave `"auths"` con `"https://index.docker.io/v1/"` adentro, hay una sesión guardada — pero no confirma que el token siga siendo válido (pudo haber sido revocado desde la web). El comando `docker info` es más confiable porque consulta contra Docker Hub en el momento.

Si usas Docker Desktop: el ícono de la ballena (barra de tareas) → tu avatar/usuario aparece ahí si estás logueado; **Sign in** si no.

Para cerrar sesión (si necesitas cambiar de cuenta): `docker logout`.

---

## Paso 1 — Crear cuenta

Si no tienes una: <https://hub.docker.com/signup>. Anota tu **usuario** (no el correo) — es el que va en `DOCKERHUB_USER` del `.env`.

---

## Paso 2 — Crear un Access Token (en vez de tu contraseña)

No uses tu contraseña de Docker Hub en la terminal ni en `docker login` — usa un **Access Token**, revocable sin cambiar tu contraseña real.

1. Entra a <https://hub.docker.com> → tu avatar (arriba a la derecha) → **Account Settings**.
2. **Security** → **Access Tokens** → **New Access Token**.
3. Descripción: algo identificable, ej. `datasentinel-local` o `datasentinel-vps`.
4. Permisos: **Read & Write** (necesitas subir imágenes, no solo bajarlas).
5. **Generate** — copia el token que aparece. **Se muestra una sola vez**, no se puede volver a ver después.

Guárdalo temporalmente en un lugar seguro (gestor de contraseñas) — lo vas a pegar en el siguiente paso.

---

## Paso 3 — Login desde tu terminal

```bash
docker login -u TU_USUARIO
```

Cuando pida `Password`, pega el **Access Token** (no tu contraseña real). Debe responder:

```text
Login Succeeded
```

Esto guarda la credencial localmente (en `~/.docker/config.json` en Linux/Mac, o el gestor de credenciales de Windows si Docker Desktop lo tiene configurado) — no necesitas repetir el login en cada sesión de terminal, solo si expira o lo cierras con `docker logout`.

Verificar que quedaste logueado:

```bash
docker info | grep Username
```

---

## Paso 4 — Configurar tu usuario en el proyecto

En el `.env` de la raíz del repo (ver [.env.docker.example](../.env.docker.example)):

```dotenv
DOCKERHUB_USER=alamdominic
IMAGE_TAG=latest
```

`DOCKERHUB_USER` debe ser el **nombre de usuario**, no el correo ni el nombre completo. Esto es lo que usa `docker-compose.yml` para nombrar las imágenes (`tu_usuario/datasentinel-api`, `tu_usuario/datasentinel-web`).

---

## Paso 5 — Crear los repositorios (opcional, se crean solos)

Si haces `docker push` a un nombre que no existe todavía en tu cuenta, Docker Hub lo crea automáticamente como **público**. Si quieres que sean **privados** desde el inicio:

1. Docker Hub → **Create repository**.
2. Nombre: `datasentinel-api` (repite para `datasentinel-web`).
3. Descripción (campo opcional, pero identifica la imagen en tu perfil de Docker Hub):
   - `datasentinel-api`: `DATA SENTINEL - Backend FastAPI (Clean Architecture), monitoreo de ejecuciones ETL en modo solo lectura.`
   - `datasentinel-web`: `DATA SENTINEL - Frontend React + Vite, dashboard de monitoreo de ejecuciones ETL.`
4. Visibilidad: **Private**.
5. **Create**.

> El plan gratuito de Docker Hub limita cuántos repositorios privados puedes tener — revisa el límite vigente en tu cuenta si planeas más de uno o dos.

---

## Paso 6 — Probar

```bash
docker compose build
docker compose push
```

> Sin `-f`, `docker compose` siempre toma **`docker-compose.yml`** (el que tiene `build:`, para construir/pushear desde tu máquina) — nunca `docker-compose.prod.yml` (ese solo se usa explícito con `-f`, en el VPS, para `pull`/`up` sin build). Los dos comandos nunca se mezclan.

Verifica en <https://hub.docker.com/repositories/TU_USUARIO> que aparezcan `datasentinel-api` y `datasentinel-web` con una imagen subida.

---

## Sobre el VPS

El `docker login` de tu computadora **no se comparte automáticamente con el VPS** — son máquinas distintas. Si tus repositorios son:

- **Públicos**: el VPS puede hacer `docker compose pull` sin login.
- **Privados**: necesitas correr `docker login -u TU_USUARIO` (con un Access Token, igual que aquí) **también en el VPS**, una sola vez, antes del primer `pull`. Ver [DEPLOY_VPS.md](DEPLOY_VPS.md) paso 5.

Recomendación: usa un Access Token **distinto** para el VPS (descripción `datasentinel-vps` en el Paso 2) — así puedes revocar el del servidor sin afectar el de tu máquina si algún día cambias de VPS o sospechas de una fuga.

---

## Troubleshooting

| Mensaje                                                              | Causa                                                                                                  | Solución                                                                                         |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `unauthorized: incorrect username or password`                       | Token mal copiado, o usaste tu contraseña real en vez del token                                        | Genera un token nuevo (Paso 2) y vuelve a intentar                                               |
| `denied: requested access to the resource is denied` al hacer `push` | `DOCKERHUB_USER` no coincide con tu usuario real, o el repo es de otra cuenta/organización sin permiso | Revisa que el nombre de imagen en `docker-compose.yml` empiece exactamente con tu usuario        |
| `toomanyrequests: You have reached your pull rate limit`             | Límite del plan gratuito de Docker Hub (por IP o por cuenta)                                           | Espera el reinicio del límite, o haz login (los pulls autenticados tienen más cupo que anónimos) |
| `docker: command not found`                                          | Docker no instalado en esa máquina                                                                     | Instala Docker Desktop (local) o `curl -fsSL https://get.docker.com \| sh` (VPS)                 |
