# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости для pygame и X11
RUN apt-get update && apt-get install -y \
    python3-pygame \
    python3-dev \
    python3-numpy \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    python3-setuptools \
    python3-pip \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxtst6 \
    libxi6 \
    x11-apps \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код игры
COPY *.py ./

# Создаем пользователя для запуска (безопасность)
RUN useradd -m -s /bin/bash gameuser && \
    chown -R gameuser:gameuser /app

# Переключаемся на пользователя
USER gameuser

# Настройки для работы с X11
ENV DISPLAY=:0
ENV PULSE_SERVER=unix:/run/user/1000/pulse/native

# Настройки pygame для работы без аудио устройств
ENV SDL_VIDEODRIVER=x11
ENV SDL_AUDIODRIVER=pulse

# Создаем директорию для X11 сокетов
RUN mkdir -p /tmp/.X11-unix

# Точка входа - запуск игры
CMD ["python3", "gui.py"]

# Метаданные
LABEL maintainer="Grisan"
LABEL description="Ball Game - интерактивная игра с физикой шариков"
LABEL version="1.0"

# Expose порта не нужен для графических приложений
# Но добавим для потенциального веб-интерфейса в будущем
EXPOSE 8080

# Добавляем health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import pygame; pygame.init(); print('OK')" || exit 1