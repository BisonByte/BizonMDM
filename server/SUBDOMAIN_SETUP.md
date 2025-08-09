# Configuración de subdominios

Este ejemplo muestra cómo redirigir múltiples subdominios a la misma aplicación
BizonMDM y permitir que el frontend cargue la configuración adecuada según el
subdominio.

## NGINX

```nginx
server {
    listen 80;
    server_name *.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Apache

```apache
<VirtualHost *:80>
    ServerName example.com
    ServerAlias *.example.com
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
</VirtualHost>
```

Con estas directivas, cualquier subdominio de `example.com` será atendido por el
mismo backend. El frontend puede detectar el subdominio y solicitar al servidor
su configuración específica.
