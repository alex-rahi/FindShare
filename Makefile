.PHONY: up down test logs

up:
	cp -n .env.example .env || true
	docker compose up --build

down:
	docker compose down

test:
	docker compose exec api pytest -q
	docker compose exec web npm test

logs:
	docker compose logs -f
