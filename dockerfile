FROM ubuntu:20.04 as builder

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        git \
        build-essential \
        autoconf \
        automake \
        libtool \
        make \
	flex \
        bison \
	pkgconf \
        libprotobuf-c-dev \
        protobuf-c-compiler \
	libprotobuf-c1 \
	libmicrohttpd-dev \
	python3-pip  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
	mkdir -p /opt/toolchain && \
	cd /opt/toolchain && \
	git clone https://github.com/collectd/collectd.git collectd-5.11 && \
	cd /opt/toolchain/collectd-5.11 && \
	./build.sh && \
	./configure --enable-cpu --enable-df --enable-memory --enable-python --enable-write_prometheus --enable-exec --enable-all-plugins=no  && \
	make && \
	make -j install


FROM ubuntu:20.04

RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install libpython3.8 libprotobuf-c1 libmicrohttpd12 \
  && apt-get clean && \
  rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/collectd  /opt/collectd

