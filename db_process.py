import sqlite3
conn = sqlite3.connect('settings.db', check_same_thread=False)  # создает файл settings.db, если его нет
cursor = conn.cursor()


"""Таблица настройки."""


cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings
    (id INTEGER PRIMARY KEY, voice TEXT, temperature TEXT, ai_model TEXT)
''')
conn.commit()

cursor.execute('''
    INSERT OR IGNORE INTO settings (id, voice, temperature, ai_model)
    VALUES (1, 'наталья', '0.7', '1.3_100k')
''')
conn.commit()


"""Таблица allowed_users."""


cursor.execute('''
    CREATE TABLE IF NOT EXISTS allowed_users
    (id INTEGER PRIMARY KEY, user_id INTEGER, settings_id INTEGER,
     FOREIGN KEY(settings_id) REFERENCES settings(id))
''')
conn.commit()


cursor.execute('''
    INSERT OR IGNORE INTO allowed_users (user_id, settings_id)
    VALUES (14835038, 1), (486707676, 1)
''')
conn.commit()


def add_allowed_user(user_id):
    cursor.execute('''
        INSERT INTO allowed_users (user_id, settings_id)
        VALUES (?, 1)
    ''', (user_id,))
    conn.commit()


def get_allowed_users():
    cursor.execute('''
        SELECT user_id FROM allowed_users WHERE settings_id = 1
    ''')
    return [row[0] for row in cursor.fetchall()]


def remove_allowed_user(user_id):
    cursor.execute('''
        DELETE FROM allowed_users 
        WHERE user_id = ? AND settings_id = 1
    ''', (user_id,))
    conn.commit()


def update_voice(new_mode):
    cursor.execute('''
        UPDATE settings
        SET voice = ?
        WHERE id = 1
    ''', (new_mode,))
    conn.commit()


def update_temperature(new_temp):
    cursor.execute('''
        UPDATE settings
        SET users = ?
        WHERE id = 1
    ''', (new_temp,))
    conn.commit()


def update_ai_model(new_model):
    cursor.execute('''
        UPDATE settings
        SET ai_model = ?
        WHERE id = 1
    ''', (new_model,))
    conn.commit()


def get_voice():
    cursor.execute('''
        SELECT voice FROM settings WHERE id = 1
    ''')
    return cursor.fetchone()[0]


def get_temperature():
    cursor.execute('''
        SELECT temperature FROM settings WHERE id = 1
    ''')
    return cursor.fetchone()[0]


def get_ai_model():
    cursor.execute('''SELECT ai_model FROM settings WHERE id = 1''')
    return cursor.fetchone()[0]

