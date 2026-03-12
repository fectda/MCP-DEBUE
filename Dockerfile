# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm

# Evitar que Python escriba archivos .pyc en disco y forzar flush de stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar 'uv' (empaquetador/instalador rápido de Python)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar configuración del proyecto
COPY pyproject.toml README.md ./
COPY src/ src/

# Sincronizar e instalar el proyecto en el entorno del sistema dentro del contenedor usando uv
RUN uv pip install --system -e .

# Crear un usuario sin privilegios para ejecutar el servidor por seguridad
RUN useradd -m mcpuser
USER mcpuser

# El entrypoint es el script generado por [project.scripts] en pyproject.toml
ENTRYPOINT ["mcp-denue"]
