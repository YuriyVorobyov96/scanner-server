Установка зависимостей:
- pip3 install -r requirements.txt

Запуск сервера с утилитами напрямую:
- python3 scanner_server.py

Запуск сервера с утилитами с помощью Docker:
- docker build -t scanner_server .
- docker run -p 3000:3000 scanner_server

Отправка запросов:
Пример1:
```
curl --location --request GET 'localhost:3000/scan' \
--header 'Content-Type: application/json' \
--data '{
    "target": "192.168.1.0",
    "count": "1"
}'
```
Пример2:
```
curl --location 'localhost:3000/sendhttp' \
--header 'Content-Type: application/json' \
--data '{
    "target": "https://blabla.free.beeceptor.com/my/api/path",
    "method": "post",
    "headers": {
        "Content-Type": "application/json"
    },
    "payload": {
        "data": "Hello Beeceptor"
    }
}'
```