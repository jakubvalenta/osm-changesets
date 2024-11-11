_python_pkg = osm_changesets

.PHONY: run
run:  ## Start the development server
	poetry run python manage.py runserver

.PHONY: setup
setup:  ## Install Python dependencies
	poetry install

.PHONY: lint
lint:  ## Lint Python code
	poetry run ruff check $(_python_pkg)
	poetry run mypy $(_python_pkg)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
