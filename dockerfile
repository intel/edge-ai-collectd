
FROM  alpine:latest as builder

RUN apk update && apk add  alpine-sdk wget git \
    py3-pip protobuf-c-dev libmicrohttpd-dev bison flex automake autoconf libtool pkgconfig
RUN apk add  curl-dev postgresql-dev python3-dev \
    libgcrypt-dev mariadb-dev zlib-dev iptables-dev \
    yajl-dev libxml2-dev openjdk8 \
    hiredis-dev varnish-dev protobuf-c-dev
RUN apk add --upgrade openssl-dev
RUN apk add --upgrade nettle-dev
RUN apk add --upgrade apk-tools-static

RUN mkdir -p /opt/toolchain && \
    cd /opt/toolchain && \
    git clone https://github.com/collectd/collectd.git collectd-5.11 && \
    cd /opt/toolchain/collectd-5.11 && \
    ./build.sh && \
    ./configure --enable-cpu --enable-df --enable-memory --enable-python --enable-write_prometheus --enable-exec --enable-all-plugins=no  && \
    make && \
    make -j install



FROM  alpine:latest

#RUN addgroup -g 101 -S nginx \
#    && adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

RUN apk update
RUN apk add --upgrade nginx-doc
RUN apk add --upgrade nettle-dev
RUN apk add --upgrade apk-tools-static
RUN apk add --upgrade openssl-dev
RUN set -x &&\
    apk add --no-cache python3-dev  libmicrohttpd  protobuf-c-dev && \
    mkdir -p /var/lib/nginx/tmp /var/lib/nginx/logs  /run/nginx && \
    ln -sf /dev/stdout /var/lib/nginx/access.log && \
    ln -sf /dev/stderr /var/lib/nginx/logs/error.log && \
    chmod -R 775 /var/lib/nginx  /run/nginx  && \
    chown -hR nginx:nginx /var/lib/nginx /var/log/nginx  /run/nginx
RUN echo `ls -al /var/log/nginx` && \
    mkdir -p /inginx && cp -R /var/lib/nginx /inginx

#RUN ls -al /var/lib/nginx && \
#    ls -al /var/lib/nginx/logs

COPY --from=builder /opt/collectd  /opt/collectd
COPY default.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf
CMD ["cp", "-R","/inginx/nginx/*", "/var/lib/nginx;"]

