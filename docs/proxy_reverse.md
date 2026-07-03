# DATA SENTINEL — Reverse proxy en el VPS (CyberPanel / OpenLiteSpeed)

Guía real de cómo se dejó el sitio publicado en el VPS de producción. **Importante:** este VPS **no usa nginx** (como asume [DEPLOY_VPS.md](DEPLOY_VPS.md)), sino **CyberPanel con OpenLiteSpeed**. El servidor web `litespeed` es dueño de los puertos 80 y 443, así que el reverse proxy se configura en el vHost de LiteSpeed, no en nginx.

---

## Contexto del servidor

| Dato | Valor |
|---|---|
| Host | `root@76.13.102.181` |
| SO | AlmaLinux 9.7 |
| Panel | CyberPanel (`/usr/local/CyberCP`) |
| Web server | OpenLiteSpeed 1.9.0 (`/usr/local/lsws`) |
| Dominio | `datasentinel.lazarza.com.mx` |
| Ruta del proyecto | `/home/datasentinel.lazarza.com.mx` |

Los contenedores ya estaban levantados y sanos:

```text
datasentinellazarzacommx-web-1   Up (healthy)   127.0.0.1:8080->80/tcp
datasentinellazarzacommx-api-1   Up (healthy)   8000/tcp   (solo red interna docker)
```

- El contenedor `web` escucha en `127.0.0.1:8080` (no expuesto a Internet).
- El nginx **interno** del contenedor `web` ya resuelve el SPA routing y proxya `/api` hacia el contenedor `api`.
- Por eso LiteSpeed solo tiene que reenviar **todo** el tráfico del dominio hacia `127.0.0.1:8080`. Un solo `context /` alcanza.

---

## El problema

Al abrir el dominio no aparecía el sitio: los contenedores corrían bien, pero **nadie conectaba el puerto 443 público con el `127.0.0.1:8080` del contenedor**. El vHost del dominio en CyberPanel se había creado como un sitio PHP normal (docroot + lsphp), no como proxy.

Diagnóstico rápido para confirmar que el contenedor sirve bien (desde el VPS):

```bash
curl -s -o /dev/null -w "web_http=%{http_code}\n" http://127.0.0.1:8080/
curl -s http://127.0.0.1:8080/api/health
# Esperado: web_http=200  y  {"status":"ok","environment":"production","database":"up"}
```

Si eso responde 200 y `database: up`, el problema es puramente el reverse proxy del host.

---

## La solución: convertir el vHost a proxy

Archivo del vHost del dominio:

```
/usr/local/lsws/conf/vhosts/datasentinel.lazarza.com.mx/vhost.conf
```

### 1. Respaldar el vhost.conf actual

```bash
cp -a /usr/local/lsws/conf/vhosts/datasentinel.lazarza.com.mx/vhost.conf \
      /usr/local/lsws/conf/vhosts/datasentinel.lazarza.com.mx/vhost.conf.bak.$(date +%s)
```

### 2. Reemplazar el contenido con este proxy

Las dos piezas clave son el bloque `extprocessor` (define el backend) y el `context /` (manda todo hacia ese backend):

```apache
docRoot                   $VH_ROOT/public_html
vhDomain                  $VH_NAME
vhAliases                 www.$VH_NAME
adminEmails               ingdatos@lazarza.com.mx
enableGzip                1

errorlog $VH_ROOT/logs/$VH_NAME.error_log {
  useServer               0
  logLevel                WARN
  rollingSize             10M
}

accesslog $VH_ROOT/logs/$VH_NAME.access_log {
  useServer               0
  logHeaders              5
  rollingSize             10M
  keepDays                10
  compressArchive         1
}

extprocessor datasentinel_web {
  type                    proxy
  address                 http://127.0.0.1:8080
  maxConns                100
  initTimeout             60
  retryTimeout            0
  respBuffer              0
}

context / {
  type                    proxy
  handler                 datasentinel_web
  addDefaultCharset       off
}

rewrite  {
  enable                  0
}

context /.well-known/acme-challenge {
  location                /usr/local/lsws/Example/html/.well-known/acme-challenge
  allowBrowse             1
  rewrite  {
     enable                  0
  }
  addDefaultCharset       off
  phpIniOverride  {
  }
}

vhssl  {
  keyFile                 /etc/letsencrypt/live/datasentinel.lazarza.com.mx/privkey.pem
  certFile                /etc/letsencrypt/live/datasentinel.lazarza.com.mx/fullchain.pem
  certChain               1
  sslProtocol             24
  enableECDHE             1
  renegProtection         1
  sslSessionCache         1
  enableSpdy              15
  enableStapling           1
  ocspRespMaxAge           86400
}
```

Notas:

- Se eliminó el `scripthandler`/`extprocessor` de lsphp y el bloque `module cache` del sitio PHP original — el dominio ya no sirve PHP, solo proxya.
- `context /.well-known/acme-challenge` se conserva para que LetsEncrypt pueda renovar el certificado.
- `vhssl` apunta al certificado ya emitido para el dominio. Si aún no existe, emítelo desde CyberPanel (SSL → Issue SSL) **antes** o el arranque de SSL fallará.

### 3. Permisos del archivo

```bash
chown lsadm:nobody /usr/local/lsws/conf/vhosts/datasentinel.lazarza.com.mx/vhost.conf
chmod 750         /usr/local/lsws/conf/vhosts/datasentinel.lazarza.com.mx/vhost.conf
```

### 4. Reiniciar OpenLiteSpeed

```bash
/usr/local/lsws/bin/lswsctrl restart
```

---

## Verificación

En el VPS (loopback, forzando el Host):

```bash
curl -sk -o /dev/null -w "root_https=%{http_code}\n" https://127.0.0.1/ -H "Host: datasentinel.lazarza.com.mx"
curl -sk https://127.0.0.1/api/health                                    -H "Host: datasentinel.lazarza.com.mx"
```

Desde fuera (dominio público real):

```bash
curl -s -o /dev/null -w "https_root=%{http_code}\n" https://datasentinel.lazarza.com.mx/
curl -s https://datasentinel.lazarza.com.mx/api/health
```

Esperado en ambos: `200` y `{"status":"ok","environment":"production","database":"up"}`.

También revisa que el CORS del API incluya el dominio (si no, el login del navegador falla):

```bash
docker exec datasentinellazarzacommx-api-1 printenv CORS_ALLOWED_ORIGINS
# Debe imprimir: https://datasentinel.lazarza.com.mx
```

`API_BASE_URL` vacío en el `.env` = mismo origen: el navegador pega a `/api` del mismo dominio y el nginx interno del contenedor `web` lo resuelve. No hay que exponer el puerto 8000.

---

## Advertencias

- **CyberPanel puede sobrescribir este `vhost.conf`.** Si editas el sitio desde el panel (SSL, PHP, rewrite rules, etc.), puede regenerar el archivo y tumbar el proxy. Si el sitio deja de cargar después de tocar el panel, restaura el bloque `extprocessor` + `context /` desde el backup (`vhost.conf.bak.*`) y vuelve a `lswsctrl restart`.
- El contenedor `web` debe seguir atado a `127.0.0.1:8080`. Si cambias `WEB_PORT` en el `.env`, actualiza también `address http://127.0.0.1:<puerto>` en el `extprocessor`.
- Renovación de SSL: al conservar el `context /.well-known/acme-challenge`, certbot/CyberPanel puede renovar sin tumbar el proxy.

---

## Plantilla reutilizable

Cualquier otra app en contenedor en este mismo VPS se publica igual: crea el sitio en CyberPanel, luego cambia su `vhost.conf` para que `extprocessor` apunte a `http://127.0.0.1:<puerto-del-contenedor>` y `context /` lo use como `handler`. El vHost `webhook.lazarza.com.mx` (contenedor en `:8001`) ya sigue este mismo patrón y sirvió de referencia.