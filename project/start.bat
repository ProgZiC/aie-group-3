@echo off
chcp 65001 >nul
echo =======================================================
echo    Запуск ML-сервиса: Прогнозирование оттока клиентов  
echo =======================================================

:: Проверка наличия папки виртуального окружения
if not exist .venv (
    echo.
    echo [1/3] Виртуальное окружение не найдено. Создаем .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo Ошибка: Убедитесь, что Python установлен и добавлен в PATH.
        pause
        exit /b
    )
) else (
    echo.
    echo [1/3] Виртуальное окружение найдено.
)

echo.
echo [2/3] Активация окружения и установка/обновление зависимостей...
call .venv\Scripts\activate
pip install -r requirements.txt

echo.
echo [3/3] Запуск FastAPI сервера...
cd src
echo API будет доступно по адресу: http://localhost:8000/
python -m uvicorn service:app --reload --port 8000

pause