FROM alpine:3.7

RUN apk --no-cache add postgresql-client && rm -rf /var/cache/apk/*

ENTRYPOINT ["psql", "-h", "server", "-p", "5432", "-U", "postgres", "-c"]
