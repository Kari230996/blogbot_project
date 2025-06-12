
📝 MyBlogBot — Telegram-бот + Django API

Телеграм-бот, связанный с REST API на Django. Позволяет:
	•	Просматривать посты
	•	Добавлять, редактировать, удалять посты
	•	Авторизоваться через логин/пароль

⸻

🚀 Быстрый старт

1. Клонировать проект и перейти в директорию

git clone https://github.com/your-username/blogbot_project.git
cd blogbot_project

2. Установить зависимости

python -m venv venv
source venv/bin/activate  # на Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Настроить переменные окружения

Переименуй .env.example в .env:

mv .env.example .env

Затем вставить нужный Telegram токен от @BotFather в поле BOT_TOKEN (можно получить от автора).

⸻

⚙️ Запуск Django API

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


⸻

🤖 Запуск Telegram-бота

В отдельном терминале:

python bot/main.py

⚠️ Важно: Django-сервер и бот должны быть запущены одновременно в разных окнах терминала.

⸻

🧠 Команды бота

Команда	Описание
/start	Приветственное сообщение
/login	Авторизация (логин + пароль)
/posts	Список всех постов
/add	Добавление поста (после авторизации)
/edit <id>	Редактирование поста
/delete <id>	Удаление поста


⸻

🔗 Основные маршруты API

Метод	Endpoint	Описание
POST	/login	Получение токена авторизации
GET	/posts	Список всех постов
GET	/posts/<id>	Получение одного поста по ID
POST	/posts	Создание поста (нужен токен)
PUT	/posts/<id>	Обновление поста (нужен токен)
DELETE	/posts/<id>	Удаление поста (нужен токен)




