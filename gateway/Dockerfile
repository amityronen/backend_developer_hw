FROM nginx:1.27-alpine

RUN rm -f /etc/nginx/conf.d/default.conf
COPY gateway/nginx.conf /etc/nginx/conf.d/melon.conf
COPY web/ /usr/share/nginx/html/
EXPOSE 80
