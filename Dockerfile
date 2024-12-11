# Используем базовый образ Python
FROM python:3.8

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы из корневой директории в контейнер
COPY . /app/

# Устанавливаем зависимости Python
RUN pip install -r requirements.txt

# Определяем команду, которая будет запущена при запуске контейнера
CMD ["python", "magage.py", "makemigrations"]
CMD ["python", "magage.py", "migrate"]
CMD ["python", "bot.py"]