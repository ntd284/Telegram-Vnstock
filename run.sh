#!/bin/bash

exec python3 ./src/main.py &
exec uvicorn src.plugin.key.tradingD:app --reload --port 8000 &
exec uvicorn src.plugin.key.tradingY:app --reload --port 8001
