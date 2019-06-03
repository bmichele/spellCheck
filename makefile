build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose stop

clean:
	docker system prune --volumes --force
