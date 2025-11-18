import psycopg2
from datetime import date as date_cls

DB_CONFIG = {
    "dbname": "app_db",
    "user": "herman",
    "password": "",
    "host": "localhost",
    "port": 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
    """)

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            task_date DATE NOT NULL,
            text VARCHAR(500) NOT NULL,
            location VARCHAR(200),
            done BOOLEAN NOT NULL DEFAULT FALSE
        );
        """
    )

    conn.commit()
    cur.close()
    conn.close()

def add_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, password)
    )

    conn.commit()
    cur.close()
    conn.close()

def get_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    cur.close()
    conn.close()
    return user


# ---- TASKS CRUD ----

def add_task(task_date: "str|date_cls", text: str, location: str | None = None):
    if isinstance(task_date, date_cls):
        task_date = task_date.isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (task_date, text, location) VALUES (%s, %s, %s) RETURNING id",
        (task_date, text, location),
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return task_id


def list_tasks(task_date: "str|date_cls", location: str | None = None):
    if isinstance(task_date, date_cls):
        task_date = task_date.isoformat()
    conn = get_connection()
    cur = conn.cursor()
    if location:
        cur.execute(
            "SELECT id, task_date, text, location, done FROM tasks WHERE task_date = %s AND (location = %s OR location IS NULL) ORDER BY id",
            (task_date, location),
        )
    else:
        cur.execute(
            "SELECT id, task_date, text, location, done FROM tasks WHERE task_date = %s ORDER BY id",
            (task_date,),
        )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"id": r[0], "task_date": r[1], "text": r[2], "location": r[3], "done": r[4]}
        for r in rows
    ]


def toggle_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done = NOT done WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()


def delete_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()