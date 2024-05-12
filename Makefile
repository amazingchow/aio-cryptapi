include .env.local .env.secret
export

VERSION  := v1.0.0
GIT_HASH := $(shell git rev-parse --short HEAD)
SERVICE  := taobao-item-price-moniter
SRC      := $(shell find . -type f -name '*.py' -not -path "./venv/*")
CURR_DIR := $(shell pwd)

.PHONY: help
help: ### Display this help screen.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: deps
deps: ### Package the runtime requirements.
	@pip freeze > requirements.txt

.PHONY: lint
lint: ### Improve your code style. (pyflakes, pycodestyle, isort)
	@echo "-> Running import sort..."
	@isort --atomic --multi-line=VERTICAL_HANGING_INDENT ${SRC}
	@echo "-> Running static code analysis..."
	@pyflakes ${SRC}
	@echo "-> Running code style check..."
	@pycodestyle ${SRC} --ignore=E101,E116,E121,E122,E123,E124,E125,E126,E128,E129,E131,E266,E402,E501,E731,W191,W293,W503

.PHONY: test
test: ### Run the tests.
	@echo "-> Running the service locally..."
	@python ./cryptapi/crypt_api.py
