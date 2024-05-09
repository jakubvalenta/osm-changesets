.PHONY: run
run:  ## Start the development server
	poetry run python manage.py runserver

.PHONY: setup
setup:  ## Install Python dependencies
	poetry install

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
