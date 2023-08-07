start:
	docker compose up --build

start_detached:
	docker compose up --build -d

stop:
	docker compose stop

formatter:
	. venv/bin/activate; command black --line-length 125 .