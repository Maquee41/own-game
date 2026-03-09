config-dev:
	cp ./.env.local ./.env

dev-start: dev-stop
	docker-compose up -d
	python3 main.py

dev-stop:
	docker-compose down

fernet-gen:
	python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key())'
