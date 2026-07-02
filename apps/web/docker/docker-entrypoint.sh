#!/bin/sh
# Hook de /docker-entrypoint.d/ de la imagen oficial nginx:alpine.
# Se ejecuta UNA vez por arranque de contenedor, antes de que la imagen base
# inicie nginx (su propio entrypoint hace el "exec nginx" despues de correr
# todos los scripts de /docker-entrypoint.d/). Este script solo genera env.js
# a partir de env.template.js con las variables reales del contenedor —
# no debe arrancar nginx ni hacer exec.
set -e

: "${API_BASE_URL:=}"

envsubst '${API_BASE_URL}' \
    < /usr/share/nginx/html/env.template.js \
    > /usr/share/nginx/html/env.js
