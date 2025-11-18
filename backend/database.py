import json
import os
from datetime import date as date_cls

# Path to local JSON cache
CACHE_FILE = "cache/tasks.json"

# Ensure cache directory exists
os.makedirs("cache", exist_ok=True)

def _load():
    if not os.path.exists(CACHE_FILE):
        return {"tasks": [], "users": []}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tasks": [], "users": []}

def _save(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---- USERS ----

def add_user(username, password):
    data = _load()
    # Check duplicate
    for u in data["users"]:
        if u["username"] == username:
            return False
    new_id = (max([u["id"] for u in data["users"]] or [0]) + 1)
    data["users"].append({"id": new_id, "username": username, "password": password})
    _save(data)
    return new_id

def get_user(username):
    data = _load()
    for u in data["users"]:
        if u["username"] == username:
            return u
    return None


# ---- TASKS ----

def create_tables():
    """
    No DB tables needed. Ensures cache file exists.
    """
    if not os.path.exists(CACHE_FILE):
        _save({"tasks": [], "users": []})


def add_task(task_date: "str|date_cls", text: str, location: str | None = None):
    if isinstance(task_date, date_cls):
        task_date = task_date.isoformat()

    data = _load()
    new_id = (max([t["id"] for t in data["tasks"]] or [0]) + 1)

    data["tasks"].append({
        "id": new_id,
        "task_date": task_date,
        "text": text,
        "location": location,
        "done": False
    })

    _save(data)
    return new_id


def list_tasks(task_date: "str|date_cls", location: str | None = None):
    if isinstance(task_date, date_cls):
        task_date = task_date.isoformat()

    data = _load()
    tasks = [t for t in data["tasks"] if t["task_date"] == task_date]

    if location:
        tasks = [t for t in tasks if t["location"] == location or t["location"] is None]

    return tasks


def toggle_task(task_id: int):
    data = _load()
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["done"] = not t["done"]
            break
    _save(data)


def delete_task(task_id: int):
    data = _load()
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    _save(data)