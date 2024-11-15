_python_pkg = osm_changesets

.PHONY: run
run:  ## Start the development server
	$(MAKE) manage args=runserver

.PHONY: worker
worker:  ## Start the Celery worker server
	DJANGO_SETTINGS_MODULE=osm_changesets.settings \
	poetry run celery -A osm_changesets.tasks worker --loglevel=INFO

.PHONY: redis
redis:  ## Start the Redis message broker
	redis-server --port 0 --unixsocket /run/user/1000/redis.sock

.PHONY: setup
setup:  ## Install Python dependencies
	poetry install

.PHONY: manage
manage:  ## Run Django's manage.py, use variable 'args' to pass arguments
	poetry run python manage.py $(args)

.PHONY: shell
shell:  ## Run Django shell
	$(MAKE) manage args=shell

.PHONY: migrate
migrate:  ## Migrate
	$(MAKE) manage args=migrate

.PHONY: makemigrations
makemigrations:  ## Make migrations
	$(MAKE) manage args="makemigrations $(_python_pkg)"

.PHONY: lint
lint:  ## Lint Python code
	poetry run ruff check $(_python_pkg)
	poetry run mypy $(_python_pkg)

.PHONY: format
format:  ## Format Python code
	poetry run ruff check --select I --fix $(_python_pkg)
	poetry run ruff format $(_python_pkg)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
