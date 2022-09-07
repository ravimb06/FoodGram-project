## Foodgram

![workflow](https://github.com/ravimb06/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Стек технологий

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

## Описание проекта
# Foodgram - «Продуктовый помощник»

Это онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект использует базу данных PostgreSQL. Проект запускается в трёх контейнерах (nginx, PostgreSQL и Django) (контейнер frontend используется лишь для подготовки файлов) через docker-compose на сервере. Образ с проектом загружается на Docker Hub.

## Запуск проекта с помощью Docker

1. Склонируйте репозиторий на локальную машину.

    ```
    git clone git@github.com:ravimb06/foodgram-project-react.git
    ```

2. Создайте .env файл в директории backend/foodgram/, в котором должны содержаться следующие переменные для подключения к базе PostgreSQL:

    ```
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY = {Ваш секретный ключ}
    ```

3. Перейдите в директорию infra/ и выполните команду для создания и запуска контейнеров.
    ```
    sudo docker compose up -d --build
    ```
> Возможна команда **$ sudo docker-compose up -d --build** (зависит от версии docker compose)

> В Windows команда выполняется без **sudo**

4. В контейнере backend выполните миграции, создайте суперпользователя и соберите статику.

    ```
    sudo docker compose exec backend python manage.py migrate
    sudo docker compose exec backend python manage.py createsuperuser
    sudo docker compose exec backend python manage.py collectstatic --no-input 
    ```

5. Загрузите в бд ингредиенты командой ниже.

    ```
    sudo docker compose exec backend python manage.py load_ingredients
    ```

6. Готово! Ниже представлены доступные адреса проекта:
    -  http://localhost/ - главная страница сайта;
    -  http://localhost/admin/ - админ панель;
    -  http://localhost/api/ - API проекта

---
## Автор
**[Али Богатырев](https://github.com/ravimb06)**

Проект развернут по адресу : **[foodgram24.ddns.net](http://foodgram24.ddns.net/recipes)**
