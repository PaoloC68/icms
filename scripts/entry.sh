#!/bin/sh -e
ICMS_WEB_PORT="${ICMS_WEB_PORT:-8080}"
ICMS_DEBUG="${ICMS_DEBUG:-False}"
ICMS_MIGRATE="${ICMS_MIGRATE:-True}"
ICMS_NUM_WORKERS="${ICMS_NUM_WORKERS:-3}"

echo "ICMS running now with debug $ICMS_DEBUG"

echo "Running migrations"
python manage.py migrate

if [ "$ICMS_DEBUG" = 'False' ]; then
  python manage.py collectstatic --noinput --traceback
  python manage.py compress --engine jinja2
fi

if [ "$ICMS_DEBUG" = 'True' ]; then
  python manage.py runserver 0:"$ICMS_WEB_PORT"
else
  gunicorn config.wsgi \
           --name icms \
           --workers "$ICMS_NUM_WORKERS" \
           --bind 0:"$ICMS_WEB_PORT"
fi
