# Foodgram

Веб-приложение «Фудграм» — продуктовый помощник для тех, кто любит готовить или хочет научиться это делать легко и непринужденно, а главное вкусно!
---
> ### Описание

Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### URL-адрес сайта доступен по ссылке:
## https://foodgram.twilightparadox.com/

---

> ### Технологии
#### Архитектура RESTful API
|Language|Framework|HTTP Server/Client|Сontainerization|CI/CD|Frontend|
|--------|---------|------------------|----------------|-----|--------|
|Python  |Django   |          Gunicorn| Docker|GitHub Actions| Node.js|
|        |Django REST Framework| Nginx|  Docker compose|     |   React|
|        |         |           Postman|                |     |        |

#### Документация к веб-приложению: https://foodgram.twilightparadox.com/redoc/
---
> ### Установка и запуск проекта:

#### Команды для консоли могут отличаться, данная инструкция адаптирована под windows, bash.

- Для развертывания локально нужно клонировать репозиторий. 
Команда для консоли из директории, куда собираемся выполнить клонирование.

```
git clone https://github.com/MendeIT/foodgram-project-react/
```
- Перейдите в репозиторий foodgram ```cd foodgram-project-react```.
- Создайте файл ```.env``` наполните данными, как указано в ```.env.example```.
- Установите Docker, после установки измените название образов в docker-compose.yml:
```
image: <DockerHub_username>/foodgram_backend
```
- Создайте образы, выполните команду из директории, где расположен docker-compose.yml:

```
docker compose up --build
```
- Разделите терминал и выполните миграции, сбор статики, а также загрузку игнредиентов и тегов для контейнера backend:
```
make test
```
- Сайт будет доступен: http://localhost:8500

Продуктивной работы!
---
> ### Автор
Алдар Дорджиев  
dordzhiev.aldar@yandex.ru