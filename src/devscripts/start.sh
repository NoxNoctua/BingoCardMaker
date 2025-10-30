#!/usr/bin/env sh
uv run uvicorn --app-dir ./src/ BingoCardMakerServer.main:app --port 8000 --host 0.0.0.0 --reload
