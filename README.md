# telegram_ai_dictaphone
telegram bot for working with long files



1. clone repo 
2. create and activate venv
3. create .env file with 
```python3
BOT_TOKEN=
OPENAI_API_KEY=
OWNER_ID=
HOOK=
```
5. install requirements 'pip install -r requirements.txt'
6. ngrok http 8000 link to HOOK in .env
7. python manage.py makemigrations
8. python manage.py migrate
9. python manage.py createsuperuser
10. python manage.py runserver
11. 127.0.0.1:8000/bot/  - setting webhook
12. ADMIN 127.0.0.1:8000/admin/