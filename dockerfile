# Установка базового образа (host OS) из DockerHub
FROM python:3.11.3-slim-bullseye

# Установка apt для управления пакетами Debian/Ubuntu
RUN apt-get update && apt-get install -y git

# Запускаем команду pip install для всех необходимых библиотек
RUN pip install -U pip

# Создаем директорию
WORKDIR /opt/project/

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt