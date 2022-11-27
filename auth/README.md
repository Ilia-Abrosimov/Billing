Ссылка на проект: https://github.com/AlexRussianPyth/Auth_sprint_2

Ссылка на проект асинхронного API: https://github.com/AlexRussianPyth/Async_API_sprint_2

## Взаимодействие с другими сервисами

Сервис аутентификации выдает клиентскому приложению JWT токены. Эти токены используются для аутетификации в других
сервисах, например сервис [API](https://github.com/AlexRussianPyth/Async_API_sprint_2). Для аутентификации в этом
сервисе API необходимо указать Bearer токен в заголовке Authorization, токен будет провалидирован самим сервисом.

Без указания токена можно увидеть только список фильмов с краткой информацией о них.

## Запуск проекта:

1. Переходим в корень проекта (в нем находится файл docker-compose.yml)
2. Создаем файл .env на основе .env_example (копируем и редактируем)
3. Запускаем создание докер-образа:

```
docker-compose up --build  
```

или с помощью Makefile:

```
make compose
```

4. Проводим миграции БД. Для этого следует зайти в контейнер с API и запустить миграции через командную строку Flask:

```
docker exec -it auth_sprint_2_auth_api_1 bash
python3 -m flask db upgrade
```

В Postgre базе создадутся все нужные миграции и партиции.

5. ОПЦИОНАЛЬНО: Создаем суперпользователя. Нужно зайти в контейнер с Flask и запустить консольную команду (не забудьте
   указать свой емэйл и пароль)

```
docker exec -it auth_sprint_2_auth_api_1 bash
python3 -m flask create-superuser your@email.com yourpassword123
```

## Особенности проекта

- В проекте используется обычный bucket-limiter, который настраивается через _.env_ файл.
- Трейсинг запросов осуществляет с помощью Jaeger. Он доступен по адресу

```
http://localhost:16686/
```

## Структура базы данных

После проведения миграций в базе данных Postgres появятся таблицы:

- alembic_version - хранит идентификатор миграции базы данных
- auth_history - пустая таблица. В ней хранится история входов пользователя.
- auth_history_<device> - таблицы-партиции для таблицы auth_history
- roles - таблица для добавленных ролей
- users - таблица для добавленных юзеров
- users_roles - связка uuid user_id и role_id_

# Список endpoints

Для тестирования ручек через [OpenAPI] необходимо перейти по адресу:

```
http://localhost:8000/
```

Представленные enpoints:

Управление ролями:

- Получение списка ролей: **GET /auth/api/v1/roles/**
- Создание роли: **POST /auth/api/v1/roles/**
- Удаление роли: **DELETE /auth/api/v1/roles/{role_id}**
- Получение роли по идентификатору: **GET /auth/api/v1/roles/{role_id}**
- Изменение роли по ее идентификатору: **PATCH /auth/api/v1/roles/{role_id}**

- Управление авторизацией:

- Авторизация пользователя: **POST /auth/api/v1/auth/login**
- Выход пользователя (помещает переданный токен в блоклист): **DELETE /auth/api/v1/auth/logout**
- Для валидного refresh-токена возвращает пару токенов access+refresh: **POST /auth/api/v1/auth/refresh**

Управление пользователями:

- Обновление логина и пароля пользователя: **PATCH /auth/api/v1/users/**
- История авторизаций пользователя: **GET /auth/api/v1/users/auth_history**
- Создание пользователя: **POST /auth/api/v1/users/register**
- Удаление роли у пользователя: **DELETE /auth/api/v1/users/{user_id}/roles**
- Получение списка ролей одного пользователя **GET /auth/api/v1/users/{user_id}/roles**
- Добавление роли пользователя **POST /auth/api/v1/users/{user_id}/roles**

## Тестирование endpoints

Тесты доступны для docker-compose.dev.yml. Запустить тесты можно следующими командами:

```
make dev-compose
docker exec -it auth_sprint_2_auth_api_1 bash
PYTHONPATH=. pytest
```
