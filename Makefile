dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

down:
	docker compose down

down-v:
	docker compose down -v        # удалить вместе с volumes

logs:
	docker compose logs -f

logs-app:
	docker compose logs -f booktracker

logs-db:
	docker compose logs -f postgres

build:
	docker compose build --no-cache

ps:
	docker compose ps

# зайти в контейнер
shell-app:
	docker compose exec booktracker bash

shell-db:
	docker compose exec postgres psql -U bookuser -d books

# перезапустить один сервис без остановки остальных
restart-app:
	docker compose restart booktracker

# пересобрать и перезапустить только приложение
redeploy:
	docker compose build booktracker
	docker compose up -d booktracker