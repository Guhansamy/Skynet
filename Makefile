.PHONY: start stop up down status
PORT = 8001

start:
	uv run uvicorn api:app --reload --reload-include "*.yml" --host 0.0.0.0 --port $(PORT)

stop:
	-fuser -k $(PORT)/tcp

up:
	sudo snap start ollama
	sudo systemctl start tailscaled
	sudo tailscale up
	sleep 3
	nohup uv run uvicorn api:app --host 0.0.0.0 --port $(PORT) > app.log 2>&1 &
	@echo "Skynet is up on port $(PORT). Logs: app.log"

down:
	-fuser -k $(PORT)/tcp
	-ollama stop qwen3.5:9b
	-ollama stop gemma3:4b
	-sudo snap stop ollama
	-sudo tailscale down
	@echo "Everything is down."

status:
	@ollama ps
	@tailscale status | head -3
	@ss -ltnp | grep -E "$(PORT)|11434" || true
