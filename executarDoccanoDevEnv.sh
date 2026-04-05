#!/bin/bash

# Abre o frontend em um novo terminal
osascript -e 'tell application "Terminal" to do script "cd Downloads/doccano/frontend && yarn dev"'

# Abre o backend em um novo terminal e executa os comandos dentro do poetry
osascript -e 'tell application "Terminal" to do script "cd Downloads/doccano/backend && poetry run python manage.py migrate && poetry run python manage.py create_roles && poetry run python manage.py create_admin --noinput --username \"admin\" --email \"admin@example.com\" --password \"password\" && poetry run python manage.py runserver"'

# Abre o worker Celery em um novo terminal e executa dentro do poetry
osascript -e 'tell application "Terminal" to do script "cd Downloads/doccano/backend && poetry run celery --app=config worker --loglevel=INFO --concurrency=1"'