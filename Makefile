default: docker-compose-up

docker-test:
	docker build -t test-social -f Dockerfile.test . && docker run test-social && docker rmi test-social -f

all:

create-network:
	@if ! docker network inspect common_network >/dev/null 2>&1; then \
		docker network create common_network; \
	fi
.PHONY: create-network

docker-image: create-network
	docker build -f ./Dockerfile -t "gateway:latest" .
.PHONY: docker-image

docker-compose-up: docker-image
	docker-compose -f docker-compose.yaml up -d --build
.PHONY: docker-compose-up

docker-compose-down:
	docker-compose -f docker-compose.yaml stop -t 20
	docker-compose -f docker-compose.yaml down --remove-orphans
.PHONY: docker-compose-down

docker-compose-logs:
	docker-compose -f docker-compose.yaml logs -f
.PHONY: docker-compose-logs