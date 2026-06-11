# Phase 1 web stub: static placeholder served by nginx, proxying /api to the gateway.
# Replaced by the React + TypeScript + Redux + MapLibre/deck.gl app in Phase 5.
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY stub/ /usr/share/nginx/html/

EXPOSE 80
