lint:
	ruff check .

format:
	ruff format .

check:
	ruff check .
	ruff format --check .

fix:
	ruff check --fix .
	ruff format .

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

collectstatic:
	python manage.py collectstatic --noinput

run:
	python manage.py runserver