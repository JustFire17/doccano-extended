#!/bin/bash

# Verificar se o serviço HTTP está respondendo
if curl -f http://localhost:8000/v1/health/ > /dev/null 2>&1; then
    echo "Healthcheck HTTP OK"
    exit 0
else
    echo "Healthcheck HTTP falhou"
    exit 1
fi 