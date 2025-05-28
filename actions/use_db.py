
import sqlite3
from typing import Dict, Optional

def init_db():
    """Инициализация базы данных и создание таблицы users."""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                city TEXT,
                hobby TEXT,
                last_session TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при инициализации базы данных: {e}")
    finally:
        conn.close()

def save_user(user_id: str, name: str, city: str, hobby: str):
    """Сохранение или обновление данных пользователя."""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, name, city, hobby, last_session)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, name, city, hobby))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении пользователя: {e}")
    finally:
        conn.close()

def get_last_user() -> Optional[Dict]:
    """Получение данных последнего пользователя."""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, name, city, hobby
            FROM users
            ORDER BY last_session DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            return {
                "user_id": result[0],
                "name": result[1],
                "city": result[2],
                "hobby": result[3]
            }
        return None
    except sqlite3.Error as e:
        print(f"Ошибка при получении последнего пользователя: {e}")
        return None
    finally:
        conn.close()