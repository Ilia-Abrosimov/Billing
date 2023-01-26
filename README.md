# Notifications


### Схема сервиса

![Схема сервиса](schema.jpg?raw=true "Схема сервиса")

### Запуск сервисов
``` 
docker-compose up --build -d
``` 

### При первом запуске для применения миграций

``` 
docker-compose exec payment_api alembic upgrade head
docker-compose exec auth_api python3 -m flask db upgrade
```

#### Для создания суперпользователя:
``` 
docker-compose exec auth_api python3 -m flask create-superuser your@email.com yourpassword123
``` 

### Эндпоинты

http://localhost:8090/api/openapi