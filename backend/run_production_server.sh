#!/bin/bash

python manage.py migrate
python manage.py load_dataset --no-verify

exec gunicorn -b 0.0.0.0:$PORT movies.wsgi:application
