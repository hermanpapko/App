# To‑Do Planner (PySide6 Desktop App)

A modern, minimalistic desktop planner with calendar, tasks, light/dark/AMOLED themes, language selector, JSON storage and smooth UI animations.

---

## 🚀 Features

### 🗓 Calendar & Tasks  
- Month calendar on the left  
- Task list with checkboxes  
- Right panel shows: **Day / Week / Month** view  
- Tasks can be:
  - Added  
  - Edited  
  - Checked/unchecked  
  - Deleted (button, context menu, Delete key)

### 🎨 UI & Themes  
- **AMOLED Dark Theme (default)**
- Light Theme  
- Smooth animated theme switching  
- Rounded UI, soft shadows, pastel markers  
- Fully redesigned language selector with custom icons  

### 🌍 Languages  
- English (default)  
- Polish  
- Russian  
- Saved in JSON settings file

### 💾 Local Cache Storage (JSON)
Everything is stored locally — no database required.

```
cache/settings.json    # theme + language
cache/tasks.json       # tasks
```

---

## 📦 Project Structure

```
App/
│
├── main.py
├── backend/
│   └── database.py        # JSON-based storage logic
│
├── ui/
│   ├── main_window.py     # full UI + themes + animations
│   └── assets/            # icons (chevrons etc.)
│
├── cache/
│   ├── settings.json
│   └── tasks.json
│
├── requirements.txt
└── README.md
```

---

# 🛠 Installation

### 1. Clone project  
```
git clone <repo-url>
cd App
```

### 2. Create virtualenv  
```
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies  
```
pip install -r requirements.txt
```

### 4. Run the app  
```
python main.py
```

---

# 📦 Building macOS App (.app + .dmg)

You can build the macOS application using PyInstaller and create a DMG manually or using create-dmg.

### ▶ Build .app  
```
python dmg_settings.py --build-app
```

Output:
```
dist/ToDoPlanner.app
```

### ▶ Build .dmg  
```
python dmg_settings.py --build-dmg
```

Output:
```
dist/ToDoPlanner.dmg
```

You can distribute it to any Mac.

---

# 🔧 Settings

Stored here:
```
cache/settings.json
```

Format:
```json
{
    "theme": "dark",
    "lang": "en"
}
```

---

# 🗂 Task Storage

```
cache/tasks.json
```

Example:
```json
[
  {
    "id": 1,
    "date": "2025-01-01",
    "text": "Buy groceries",
    "done": false
  }
]
```

---

# 🤝 Contributing  
Pull requests are welcome.