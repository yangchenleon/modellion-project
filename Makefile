 .PHONY: up down logs restart backend-shell frontend-shell

 up:
 	docker compose up -d --build
 	docker compose logs -f backend

 down:
 	docker compose down -v

 logs:
 	docker compose logs -f --tail=200

 restart:
 	docker compose down
 	docker compose up -d --build

 backend-shell:
 	docker compose exec backend bash

 frontend-shell:
 	docker compose exec frontend sh
