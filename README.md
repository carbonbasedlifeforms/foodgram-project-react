# Дипломный проект FoodGram

![Github actions](https://github.com/carbonbasedlifeforms/foodgram-project-react/actions/workflows/foodgram_workflow.yaml/badge.svg)

Foodgram реализует функционал продуктового помощника - сайт, многопользовательская система для публикации рецептов блюд
авторизованными пользователями со встроенным механизмом рещистрации пользователей, публикацией рецептов с использованием предустановленных ингредиентов блюд, с возможностями подписки на других авторов, добавления рецептов в избранное, подготовки списка покупок на основе рецепта и его скачивания с сайта.

### Проект развернутый в яндекс облаке:
http://pogromism.sytes.net

**Как запустить проект локально:**
Склонируйте репозиторий:
```bash
git clone git@github.com:carbonbasedlifeforms/foodgram-project-react.git
```

Заполните файл с переменными окружения .env
DB_ENGINE=*<тип БД>*

DB_NAME=*<имя базы данных>*

POSTGRES_USER=*<логин для подключения к базе данных>*

POSTGRES_PASSWORD=*<пароль для подключения к БД>*

DB_HOST=*<название сервиса (контейнера)>*

DB_PORT=*<порт для подключения к БД>*

Перейтите в каталог foodgram-project-react/infra
```bash
cd ./foodgram-project-react/infra
```

Соберите образ с помощью docker-compose
```bash
docker-compose up -d --build
```

Выполните миграции:
```bash 
docker-compose exec backend python manage.py migrate
```

Соберите статику в проекте:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

Создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

Заполните базу данных:
```bash
docker-compose exec backend python manage.py loaddata fixtures.json
```

Проект доступен по адресу:
```bash
http://localhost
```

Документация к api доступна по адресу:
```
http://localhost/api/docs/redoc.html
http://localhost/api/docs/swagger.html
```