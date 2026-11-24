.PHONY: start stop

start:
	uv run uvicorn api:app --reload --reload-include "*.yml" --host 0.0.0.0 --port 8001

stop:
	fuser -k 8001/tcp