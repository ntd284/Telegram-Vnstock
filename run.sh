#!/bin/bash
cron
exec python3 ./src/main.py &
exec uvicorn src.plugin.key.tradingD:app --reload --port 8000
