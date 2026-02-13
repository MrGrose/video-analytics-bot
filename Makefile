
.PHONY: up down stop restart logs ps clean help 

up:
	docker compose up -d db
	docker compose run --rm loader
	docker compose up -d bot

down:
	docker compose down -v

stop:
	docker compose stop

restart: stop up

logs:
	docker compose logs -f bot

ps:
	docker compose ps

clean:
	docker compose down -v --remove-orphans && docker system prune -f

help:
	@echo "Команды: up, down, stop, restart, logs, ps, clean"


	