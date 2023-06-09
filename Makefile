SHELL:=/usr/bin/env bash

.PHONY: install
install:
	sudo usermod -aG docker ${USER}
	source ~/.bashrc
	sudo systemctl start docker
	curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" 
	@unzip -q awscliv2.zip
	sudo ./aws/install --update
	rm awscliv2.zip
	rm -r ./aws
	newgrp docker

.PHONY: docker_containers_poetry
docker_containers_poetry:
	-python -m ensurepip --upgrade
	python -m pip install poetry
	docker info
	-docker run -d -p 5672:5672 --name=rabbitmq rabbitmq
	-docker run -d -p 8182:8182 --name=gremlin-server tinkerpop/gremlin-server:3.6.1
	-docker run --rm -d --net=host --name=gremlin-visualizer prabushitha/gremlin-visualizer:latest
	-docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
	python -m poetry install
	python -m poetry shell
	python -m poetry build


.PHONY: uninstall
uninstall:
	python -m poetry shell
	deactivate .
	-docker stop rabbitmq
	-docker stop redis-stack
	-docker stop gremlin-server
	-docker stop gremlin-visualizer

.PHONY: lint
lint:
	python -m poetry run flake8 .
	python -m poetry run doc8 -q docs

.PHONY: unit
unit:
	python -m poetry run pytest

.PHONY: package
package:
	python -m poetry check
	python -m poetry run pip check
	python -m poetry run safety check --full-report

.PHONY: test
test: lint package unit

.DEFAULT:
	@cd docs && $(MAKE) $@

