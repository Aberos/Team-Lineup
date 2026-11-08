#!/bin/sh
set -e

cd /app/frontend
npm install --no-audit --no-fund
rm -rf dist
npm run build:watch &

until [ -f dist/index.html ]; do
  sleep 1
done

cd /app
python manage.py migrate --noinput
python manage.py seed_defaults
exec python -m debugpy --listen "0.0.0.0:${DEBUG_PORT}" \
  manage.py runserver "0.0.0.0:${APP_PORT}" --noreload
