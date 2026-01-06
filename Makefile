build_dev:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-mailcatcher.yml \
		-f docker-compose-local.yml \
		build

dev:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-mailcatcher.yml \
		-f docker-compose-local.yml \
		up -d

down_dev:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-mailcatcher.yml \
		-f docker-compose-local.yml \
		down -v --remove-orphans

build_prod:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-prod.yml \
		build

prod:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-prod.yml \
		up -d

down_prod:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-prod.yml \
		down -v --remove-orphans

build_e2e:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-mailcatcher.yml \
		-f docker-compose-prod.yml \
		-f docker-compose-playwright.yml \
		build

e2e:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-mailcatcher.yml \
		-f docker-compose-prod.yml \
		-f docker-compose-playwright.yml \
		up -d

down_e2e:
	docker compose \
		-f docker-compose-base.yml \
		-f docker-compose-mailcatcher.yml \
		-f docker-compose-prod.yml \
		-f docker-compose-playwright.yml \
		down -v --remove-orphans
