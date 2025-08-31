# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей (если есть)
# COPY requirements.txt .

# Устанавливаем зависимости (если есть)
# RUN pip install -r requirements.txt

# Копируем код приложения
COPY . .

# Открываем порт (если нужно)
# EXPOSE 8000

# Запускаем приложение
CMD ["python", "main.py"]
