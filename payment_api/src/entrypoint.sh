#!/bin/sh
alembic upgrade head
gunicorn -k uvicorn.workers.UvicornWorker --bind "0.0.0.0:8000" main:app
