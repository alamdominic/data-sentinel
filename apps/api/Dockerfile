# DATA SENTINEL API — imagen de produccion.
# Toda la configuracion (DB_HOST, AUTH_SECRET_KEY, etc.) se inyecta como
# variables de entorno al crear el contenedor — no hay nada de config
# horneado en esta imagen.
FROM python:3.11-slim AS base

WORKDIR /app

# Capa de dependencias separada del codigo para aprovechar cache de Docker:
# solo se reinstalan deps si cambia pyproject.toml, no en cada cambio de codigo.
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

COPY app ./app

RUN useradd --create-home --shell /bin/false datasentinel
USER datasentinel

EXPOSE 8000

# Health check propio (no depende de nginx): docker/compose puede usar esto
# para saber si el contenedor esta realmente sirviendo, no solo "arrancado".
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
