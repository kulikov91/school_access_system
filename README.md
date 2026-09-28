# СКУД школы

Стек: Python, Flask, Jinja/HTML/CSS, PostgreSQL, psycopg, pytest.

## Подготовка базы данных
Проект разрабатывался поэтапно, поэтому изменения структуры базы данных
оформлены отдельными SQL-миграциями.

### Первоначальное создание базы данных

Создайте базу данных:

createdb -U postgres school_access

Выполнить последовательно исходную схему и миграции:

    psql -h 127.0.0.1 -p 5432 -U postgres -d school_access -f database/schema.sql

    psql -h 127.0.0.1 -p 5432 -U postgres -d school_access -f database/stage2_migration.sql

    psql -h 127.0.0.1 -p 5432 -U postgres -d school_access -f database/stage3_migration.sql

## Запуск

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    export DB_PASSWORD='пароль PostgreSQL'
    python main.py

Демонстрационные пользователи: admin, director, deputy, security, parent. Пароль: demo123.

## Уведомления
При регистрации входа или выхода система формирует уведомление родителю и сохраняет его в PostgreSQL. В
нешняя доставка сообщений в текущую версию проекта не входит. 
Интеграция с Telegram, SMS или push рассматривается как перспектива развития.

## Тесты

    pytest -q

## Реализовано
Авторизация и 5 ролей; 
RFID/NFC-эмуляция; 
Журнал IN/OUT; 
CRUD учащихся/родителей/меток; 
Поиск и фильтры; 
Формирование и хранение уведомлений; 
Аудит с фиксацией старого/нового значения; 
pytest.
