from database.connection import get_connection
from werkzeug.security import check_password_hash, generate_password_hash

DEMO_USERS = [
    ('admin', 'Системный администратор', 'sysadmin', None),
    ('director', 'Директор школы', 'director', None),
    ('deputy', 'Завуч', 'deputy', None),
    ('security', 'Охранник', 'security', None),
    ('parent', 'Иванова Мария Петровна', 'parent', 1),
]


def ensure_demo_users():
    """Создает демонстрационные учетные записи Stage 2, если их еще нет."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            for username, full_name, role, id_parent in DEMO_USERS:
                cursor.execute('SELECT 1 FROM users WHERE username = %s', (username,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        '''INSERT INTO users (username, password_hash, full_name, role, id_parent)
                           VALUES (%s, %s, %s, %s, %s)''',
                        (username, generate_password_hash('demo123'), full_name, role, id_parent),
                    )
        connection.commit()


def authenticate(username: str, password: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''SELECT id_user, username, password_hash, full_name, role, id_parent
                   FROM users WHERE username = %s AND is_active = TRUE''',
                (username.strip(),),
            )
            row = cursor.fetchone()
    if row is None or not check_password_hash(row[2], password):
        return None
    return {
        'id_user': row[0], 'username': row[1], 'full_name': row[3],
        'role': row[4], 'id_parent': row[5],
    }
