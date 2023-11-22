test:
	docker compose exec backend python manage.py migrate --noinput
	docker compose exec backend python manage.py loadingredientstags
	docker compose exec backend python manage.py collectstatic --noinput
	sudo docker compose exec backend cp --recursive --update /app/collected_static/. /backend_static/static/

deploy:
	sudo docker compose -f docker-compose.production.yml pull
	sudo docker compose -f docker-compose.production.yml down
	sudo docker compose -f docker-compose.production.yml up -d
	sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate --noinput
	sudo docker compose -f docker-compose.production.yml exec backend python manage.py loadingredientstags
	sudo docker compose -f docker-compose.production.yml exec backend cp --recursive --update /app/collected_static/. /backend_static/static/