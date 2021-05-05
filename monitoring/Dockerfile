FROM  grafana/grafana:latest

USER root

# Install INFN-CLOUD CAs
RUN wget "https://crt.sh/?d=2475254782" -O /usr/local/share/ca-certificates/ca.crt && \
    update-ca-certificates
