FROM alpine:3.7

RUN apk add --no-cache build-base python3 python3-dev py3-lxml && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

# lxml kann man mit py3-lxml installieren
# angeblich kann man psycopg2 mit apk add py3-psycopg2 installieren...
# aber dann verteilen sich die ganzen packages ja auf apk und pip3
# vllt ne file build_deps.txt oder so machen für die ganzen dinger
