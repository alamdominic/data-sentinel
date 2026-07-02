"""Script administrativo: crear usuario autorizado con password bcrypt.

Las contrasenas solo se administran por este medio; la aplicacion web
no permite cambiarlas (ver SPEC.md).

Uso:
    python scripts/create_user.py correo@lazarza.com.mx "Nombre Completo" [role]

Pide la contrasena por consola y genera el INSERT listo para ejecutar,
o lo ejecuta directo si DATABASE_ADMIN_URL esta definida.
"""
import getpass
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from app.domain.value_objects.institutional_email import InstitutionalEmail  # noqa: E402
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher  # noqa: E402

def _load_scripts_env() -> None:
    """Carga scripts/.env si existe (sin dependencia de python-dotenv)."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_scripts_env()
ALLOWED_DOMAIN = os.environ.get("AUTH_ALLOWED_EMAIL_DOMAIN", "lazarza.com.mx")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    email_arg, full_name = sys.argv[1], sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "viewer"

    email = InstitutionalEmail(value=email_arg, allowed_domain=ALLOWED_DOMAIN)
    password = getpass.getpass("Password: ")
    if len(password) < 8:
        print("La contrasena debe tener al menos 8 caracteres")
        return 1
    if password != getpass.getpass("Confirmar password: "):
        print("Las contrasenas no coinciden")
        return 1

    password_hash = BcryptPasswordHasher().hash(password)
    query = (
        "INSERT INTO etl_execution_aws.app_users (email, password_hash, full_name, role) "
        "VALUES (%s, %s, %s, %s) "
        "ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash, "
        "full_name = EXCLUDED.full_name, role = EXCLUDED.role, updated_at = CURRENT_TIMESTAMP;"
    )

    admin_url = os.environ.get("DATABASE_ADMIN_URL")
    if admin_url:
        import psycopg

        with psycopg.connect(admin_url) as conn:
            conn.execute(query, (email.value, password_hash, full_name, role))
        print(f"Usuario {email.value} creado/actualizado (role={role}).")
    else:
        print("DATABASE_ADMIN_URL no definida. Ejecuta manualmente:")
        print(
            query.replace("%s", "'{}'").format(email.value, password_hash, full_name, role)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
