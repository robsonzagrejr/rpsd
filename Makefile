install:
	poetry install

update:
	poetry update

server:
	poetry run python src/server.py

app:
	poetry run python app.py
