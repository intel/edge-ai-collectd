SHELL=/bin/bash

CA_KEY=ca.key
CA_CRT=ca.crt

SERVER_KEY=server.key
SERVER_CSR=server.csr
SERVER_CRT=server.crt

DNS_SAN=DNS:*.collectd-svc.default.svc.cluster.local
DNS_SUBJECT=collectd-svc.default.svc.cluster.local

SHELL_EXPORT = $(foreach v,$(MAKE_ENV),$(v)='$($(v))' )


.PHONY: all default

.DEFAULT_GOAL := $(SERVER_CRT)

$(CA_KEY) $(CA_CRT):
	@echo "Generating CA..."
	@openssl req -x509 -sha384 -new -nodes -days 365 -newkey rsa:4096 -keyout $(CA_KEY) -out $(CA_CRT) -subj "/C=SG/ST=SG/O=MyOrg, Inc./CN=ca";

$(SERVER_KEY):
	@echo "Generating server key..."
	@openssl genrsa -out $(SERVER_KEY) 4096;

$(SERVER_CSR): $(SERVER_KEY)
	@echo "Generating server csr..."
	@openssl req -new -sha384 \
	-key $(SERVER_KEY) \
	-subj "/C=SG/ST=SG/O=MyOrg, Inc./CN=$(DNS_SUBJECT)" \
	-reqexts SAN \
	-config <(cat /etc/ssl/openssl.cnf <(printf "\n[SAN]\nsubjectAltName=$(DNS_SAN)")) \
	-out $(SERVER_CSR)

$(SERVER_CRT): $(SERVER_CSR) $(SERVER_KEY) $(CA_KEY) $(CA_CRT)
	@echo "Generating server crt..."
	@openssl x509 -req \
	-extfile <(printf "subjectAltName=$(DNS_SAN)") \
	-in $(SERVER_CSR) -CA $(CA_CRT) -CAkey $(CA_KEY) -CAcreateserial -out $(SERVER_CRT) -days 365 -sha384


default: $(SERVER_CRT)

all:
	@echo "Make all"

