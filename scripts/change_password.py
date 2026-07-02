"""Script administrativo: cambio de contrasena de un usuario existente.

Uso exclusivo del ingeniero de datos, en local. La aplicacion web nunca
cambia contrasenas (ver SPEC.md).

IMPORTANTE: bcrypt es hashing de una via. No existe forma de "descifrar"
un hash para recuperar la contrasena original. El flujo soportado es
RESET: se asigna una contrasena nueva.

Uso:
    # pedir la nueva contrasena por consola (no queda en historial)
    python scripts/change_password.py usuario@lazarza.com.mx

    # generar una contrasena aleatoria segura y mostrarla una sola vez
    python scripts/change_password.py usuario@lazarza.com.mx --generate

Conexion: usa DATABASE_ADMIN_URL (definida en scripts/.env o en el
ambiente). Sin ella, imprime el UPDATE listo para ejecutar manualmente.
"""
import getpass
import os
import secrets
import string
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from app.domain.value_objects.institutional_email import InstitutionalEmail  # noqa: E402
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher  # noqa: E402

ALLOWED_DOMAIN = os.environ.get("AUTH_ALLOWED_EMAIL_DOMAIN", "lazarza.com.mx")
MIN_PASSWORD_LENGTH = 8
GENERATED_LENGTH = 16


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


def _generate_password() -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%&*-_"
    return "".join(secrets.choice(alphabet) for _ in range(GENERATED_LENGTH))


def main() -> int:
    _load_scripts_env()

    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    generate = "--generate" in sys.argv
    if len(args) != 1:
        print(__doc__)
        return 1

    email = InstitutionalEmail(value=args[0], allowed_domain=ALLOWED_DOMAIN)

    if generate:
        password = _generate_password()
    else:
        password = getpass.getpass("Nueva contrasena: ")
        if len(password) < MIN_PASSWORD_LENGTH:
            print(f"La contrasena debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")
            return 1
        if password != getpass.getpass("Confirmar contrasena: "):
            print("Las contrasenas no coinciden")
            return 1

    password_hash = BcryptPasswordHasher().hash(password)
    query = (
        "UPDATE etl_execution_aws.app_users "
        "SET password_hash = %s, updated_at = CURRENT_TIMESTAMP "
        "WHERE lower(email) = lower(%s);"
    )

    admin_url = os.environ.get("DATABASE_ADMIN_URL")
    if admin_url:
        import psycopg

        with psycopg.connect(admin_url) as conn:
            result = conn.execute(query, (password_hash, email.value))
            if result.rowcount == 0:
                print(f"No existe usuario con correo {email.value}")
                return 1
        print(f"Contrasena actualizada para {email.value}.")
    else:
        print("DATABASE_ADMIN_URL no definida. Ejecuta manualmente:")
        print(
            "UPDATE etl_execution_aws.app_users "
            f"SET password_hash = '{password_hash}', updated_at = CURRENT_TIMESTAMP "
            f"WHERE lower(email) = lower('{email.value}');"
        )

    if generate:
        print("\nContrasena generada (entregala por canal seguro; no se puede recuperar despues):")
        print(password)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
