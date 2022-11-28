#!/bin/bash
. /opt/taglink-api/.venv-fastapi/bin/activate
uvicorn --host 0.0.0.0 main:app --root-path /api --reload