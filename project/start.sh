#!/bin/bash

echo "======================================================="
echo "   Запуск ML-сервиса: Прогнозирование оттока клиентов  "
echo "======================================================="

# Проверка наличия папки виртуального окружения
if [ ! -d ".venv" ]; then
    echo -e "\n[1/3] Виртуальное окружение не найдено. Создаем .venv..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Ошибка: Убедитесь, что python3 установлен."
        exit 1
    fi
else
    echo -e "\n[1/3] Виртуальное окружение найдено."
fi

echo -e "\n[2/3] Активация окружения и установка/обновление зависимостей..."
source .venv/bin/activate
pip install -r requirements.txt

echo -e "\n[3/3] Запуск FastAPI сервера..."
cd src || exit
echo "API будет доступно по адресу: http://localhost:8000/"
python -m uvicorn service:app --reload --port 8000