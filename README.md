# Project_temp
Актуальный темплайт для разработчки на Fast api

Для работы требуется:
- PostgreSQL
- Redis
- NATS

Команда запуска fast stream

`
poetry run faststream run src.__main__:faststream --reload
`

## Переменные

## Подключение к БД
| Название     | Описание                                                                                   | Значение по-умолчанию                                  |
|--------------|--------------------------------------------------------------------------------------------|--------------------------------------------------------|
| `DB_URI`     | Строка подключения к базе данных PostgreSQL. Формат: `postgresql+asyncpg://{user}:{pass}@{host}:{port}/{db}` | `postgresql+asyncpg://{}:{}@{}:{}/{}`
| `DB_HOST`    | Хост базы данных PostgreSQL                                                                | `localhost`
| `DB_PORT`    | Порт базы данных PostgreSQL                                                                | `5432`
| `DB_USER`    | Имя пользователя для подключения к базе данных                                             | `test`
| `DB_NAME`    | Имя базы данных PostgreSQL                                                                 | `test`
| `DB_PASSWORD`| Пароль для подключения к базе данных                                                       | `test`

## Настройки сервера
| Название        | Описание                                                    | Значение по-умолчанию                    |
|-----------------|-------------------------------------------------------------|------------------------------------------|
| `SERVER_HOST`   | Хост, на котором запускается сервер                         | `0.0.0.0`
| `SERVER_PORT`   | Порт, на котором запускается сервер                         | `8000`
| `SERVER_METHODS`| Список методов HTTP, которые поддерживает сервер            | `["OPTIONS", "DELETE", "POST", "GET", "PATCH"]`
| `SERVER_INTERNAL_API_TOKEN`   | Внутренний токен                              | `internal_auth_token`

## Настройки Redis
| Название        | Описание                                        | Значение по-умолчанию |
|-----------------|-------------------------------------------------|-----------------------|
| `REDIS_HOST`    | Хост Redis                                      | `localhost`
| `REDIS_PORT`    | Порт Redis                                      | `6370`
| `REDIS_PASSWORD`| Пароль для подключения к Redis (если требуется) | `password`

## Настройки Nats
| Название        | Описание                                        | Значение по-умолчанию                 |
|-----------------|-------------------------------------------------|---------------------------------------|
| `NATS_SERVERS`  | Натс Серверы                                    | `["nats://localhost:4220"]`
| `NATS_USER`     | Натс юзер                                       | `admin`
| `NATS_PASSWORD` | Натс пороль                                     | `123456789123456789123456789123456789`

## Настройки приложения
| Название                              | Описание                                                    | Значение по-умолчанию             |
|---------------------------------------|-------------------------------------------------------------|-----------------------------------|
| `LOG_LEVEL`                           | Уровень логирования                                         | `INFO`                            |
| `PROJECT_NAME`                        | Название проекта                                            | `risa_project`                        |
| `PROJECT_VERSION`                     | Версия проекта                                              | `0.1.0`                           |
| `CIPHER_SECRET_KEY`                   | Ключ шифрования, для шифрования приватного ключа            |                                   |
| `CIPHER_PUBLIC_KEY`                   | Ключ шифрования, для шифрования публичного ключа            |                                   |
| `CIPHER_ACCESS_TOKEN_EXPIRE_SECONDS`  | Время жизни access токена в секундах                        | `1800`                            |
| `CIPHER_REFRESH_TOKEN_EXPIRE_SECONDS` | Время жизни refresh токена в секундах                       | `604800`                          |
| `AESCIPHER_SECRET_KEY`                | Ключ шифрования, для подписи токена бота                    |                                   |

### 1. Приватный aescipher
- openssl genpkey -algorithm Ed25519 -out private.pem && cat private.pem | base64

### 2. Публичный aescipher
- openssl pkey -in private.pem -pubout -out public.pem && cat public.pem | base64

### 3. generate uuid for internal api token:
- python -c "import uuid; print(uuid.uuid4())"

### 4. For proper working pre-commit you should use the command below:
- pre-commit install --install-hooks
