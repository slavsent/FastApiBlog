# FastApiBlog
Реализация асинхронного API по ведению блогов с использованием Python и FastAPI

Как запустить:
требуется наличие postgreSQL
в .my-env надо добавить данные по образцу example.env
установить зависимости из requirements.txt
Выполнить
python main.py

или
.my-env изменять не надо
Выполнить:
docker-compose --env-file .my-env up -d --build
и перейдите на http://127.0.0.1:8000/docs


