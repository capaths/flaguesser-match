#!/bin/sh

until nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

until nc -z ${DB_HOST} ${DB_PORT}; do
    echo "$(date) - waiting for postgres..."
    sleep 1
done

echo "Starting service"
nameko run --config config.yaml match.service
