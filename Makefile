build_dev:
	docker compose -f docker-compose-base.yml -f docker-compose-local.yml build

build_prod:
	docker compose -f docker-compose-base.yml -f docker-compose-prod.yml build

dev:
	docker compose -f docker-compose-base.yml -f docker-compose-local.yml up -d

prod:
	docker compose -f docker-compose-base.yml -f docker-compose-prod.yml up -d

down_dev:
	docker compose -f docker-compose-base.yml -f docker-compose-local.yml down -v --remove-orphans

down_prod:
	docker compose -f docker-compose-base.yml -f docker-compose-prod.yml down -v --remove-orphans
