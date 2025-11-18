from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDateEdit, QListWidget, QListWidgetItem, QMessageBox,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import QDate
from backend.database import add_task, list_tasks, toggle_task, delete_task
from backend.logic import get_weather, WeatherError

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Meteo Planner PRO")
        self.setMinimumSize(900, 600)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)
        header = self.create_header()
        main_layout.addWidget(header)

        controls = self.create_controls()
        main_layout.addWidget(controls)

        weather = self.create_weather_panel()
        main_layout.addWidget(weather)

        tasks = self.create_tasks_panel()
        main_layout.addWidget(tasks)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Применяем единый тёмный стиль (только dark theme)
        self.apply_styles()

        # Initial load
        self.date_edit.setDate(QDate.currentDate())
        self.location_edit.setText("Warszawa")
        self.refresh_all()

    def create_header(self):
        header = QWidget()
        header.setObjectName("headerBar")
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        logo = QLabel("Meteo Planner PRO")
        logo.setObjectName("appTitle")

        layout.addWidget(logo)
        layout.addStretch()

        # Тёмная тема всегда активна — переключателя темы нет

        header.setLayout(layout)
        # Subtle shadow for depth
        self._apply_shadow(header, radius=16, y_offset=3, blur=24, color=(14, 165, 233, 80))
        return header

    def create_controls(self):
        box = QWidget()
        box.setObjectName("controlsBar")
        layout = QHBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Lokalizacja (np. Warszawa)")
        layout.addWidget(QLabel("Lokalizacja:"))
        layout.addWidget(self.location_edit)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        layout.addWidget(QLabel("Data:"))
        layout.addWidget(self.date_edit)

        self.refresh_btn = QPushButton("⟲ Odśwież")
        self.refresh_btn.clicked.connect(self.refresh_all)
        layout.addWidget(self.refresh_btn)

        layout.addStretch()
        box.setLayout(layout)
        return box

    def create_weather_panel(self):
        box = QWidget()
        box.setObjectName("weatherPanel")
        layout = QHBoxLayout()
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(18)

        self.lbl_weather_loc = QLabel("📍 –")
        self.lbl_t = QLabel("🌡️ Tmax/Tmin: – / – °C")
        self.lbl_t.setObjectName("tempLabel")
        self.lbl_p = QLabel("🌧️ Opady: – mm")
        self.lbl_w = QLabel("💨 Wiatr max: – km/h")

        layout.addWidget(self.lbl_weather_loc)
        layout.addWidget(self.lbl_t)
        layout.addWidget(self.lbl_p)
        layout.addWidget(self.lbl_w)
        layout.addStretch()
        box.setLayout(layout)
        self._apply_shadow(box)
        return box

    def create_tasks_panel(self):
        box = QWidget()
        box.setObjectName("tasksPanel")
        v = QVBoxLayout()
        v.setContentsMargins(18, 14, 18, 14)
        v.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Dodaj zadanie…")
        self.btn_add_task = QPushButton("＋ Dodaj")
        self.btn_add_task.setObjectName("secondaryButton")
        self.btn_add_task.clicked.connect(self.add_task_clicked)
        row.addWidget(self.task_input)
        row.addWidget(self.btn_add_task)

        self.tasks_list = QListWidget()
        self.tasks_list.setAlternatingRowColors(True)
        btns = QHBoxLayout()
        self.btn_toggle = QPushButton("✓ Ukończone")
        self.btn_toggle.setObjectName("secondaryButton")
        self.btn_delete = QPushButton("🗑 Usuń")
        self.btn_delete.setObjectName("dangerButton")
        self.btn_toggle.clicked.connect(self.toggle_task_clicked)
        self.btn_delete.clicked.connect(self.delete_task_clicked)
        btns.addWidget(self.btn_toggle)
        btns.addWidget(self.btn_delete)
        btns.addStretch()

        v.addLayout(row)
        v.addWidget(self.tasks_list)
        v.addLayout(btns)
        box.setLayout(v)
        self._apply_shadow(box)
        return box

    # ---- Actions ----
    def refresh_all(self):
        self.load_weather()
        self.load_tasks()

    def current_date_str(self):
        return self.date_edit.date().toString("yyyy-MM-dd")

    def current_location(self):
        return self.location_edit.text().strip() or "Warszawa"

    def load_weather(self):
        try:
            w = get_weather(self.current_location(), self.current_date_str())
            self.lbl_weather_loc.setText(f"📍 {w.get('location_name') or self.current_location()}")
            tmax = w.get("tmax")
            tmin = w.get("tmin")
            self.lbl_t.setText(f"🌡️ Tmax/Tmin: {tmax} / {tmin} °C")
            self.lbl_p.setText(f"🌧️ Opady: {w.get('precipitation')} mm")
            self.lbl_w.setText(f"💨 Wiatr max: {w.get('wind_max')} km/h")
        except WeatherError as e:
            QMessageBox.warning(self, "Pogoda", str(e))

    def load_tasks(self):
        self.tasks_list.clear()
        tasks = list_tasks(self.current_date_str(), self.current_location())
        for t in tasks:
            prefix = "✓ " if t["done"] else "• "
            item = QListWidgetItem(prefix + t["text"])
            item.setData(256, t["id"])  # Qt.UserRole
            # Stylizacja ukończonych задач: перечёркивание и приглушённый цвет
            f = item.font()
            f.setStrikeOut(bool(t["done"]))
            item.setFont(f)
            if t["done"]:
                from PySide6.QtGui import QColor
                item.setForeground(QColor("#6b7280"))
            self.tasks_list.addItem(item)

    def add_task_clicked(self):
        txt = self.task_input.text().strip()
        if not txt:
            return
        add_task(self.current_date_str(), txt, self.current_location())
        self.task_input.clear()
        self.load_tasks()

    def _selected_task_id(self):
        item = self.tasks_list.currentItem()
        if not item:
            return None
        return item.data(256)

    def toggle_task_clicked(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        toggle_task(int(tid))
        self.load_tasks()

    def delete_task_clicked(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        delete_task(int(tid))
        self.load_tasks()

    # ---- Styles ----
    def apply_styles(self):
        stylesheet = """
        /* Base */
        QWidget { font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, Arial; font-size: 14px; color: #e5e7eb; background: #0b1220; }

        /* Header */
        #headerBar { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0ea5e9, stop:1 #22d3ee); border-radius: 12px; }
        #headerBar QLabel#appTitle { color: white; font-size: 22px; font-weight: 700; letter-spacing: 0.3px; }

        /* Controls */
        #controlsBar { background: #0f172a; border: 1px solid #1f2a44; border-radius: 12px; }
        #controlsBar QLabel { color: #cbd5e1; font-weight: 600; }
        QLineEdit, QDateEdit { background: #0b1220; color: #e5e7eb; border: 1px solid #26334d; border-radius: 10px; padding: 9px 12px; }
        QLineEdit:focus, QDateEdit:focus { border: 1px solid #38bdf8; }

        /* Buttons */
        QPushButton { background: #0ea5e9; color: white; border: none; border-radius: 10px; padding: 9px 16px; font-weight: 600; }
        QPushButton:hover { background: #0284c7; }
        QPushButton:pressed { background: #0369a1; }
        QPushButton:focus { outline: none; border: 2px solid #38bdf8; }
        QPushButton#secondaryButton { background: #1f2a44; color: #e5e7eb; }
        QPushButton#secondaryButton:hover { background: #2a3755; }
        QPushButton#dangerButton { background: #ef4444; }
        QPushButton#dangerButton:hover { background: #dc2626; }

        /* Panels */
        #weatherPanel, #tasksPanel { background: #0f172a; border: 1px solid #1f2a44; border-radius: 14px; }
        #weatherPanel QLabel { color: #e2e8f0; font-weight: 600; }
        #weatherPanel QLabel#tempLabel { font-size: 16px; font-weight: 700; }

        /* Tasks list */
        QListWidget { border: 1px solid #1f2a44; border-radius: 12px; padding: 6px; background: #0b1220; }
        QListWidget::item { padding: 8px 10px; }
        QListWidget::item:hover { background: #0f172a; }
        QListWidget::item:selected { background: #0ea5e955; color: #c7d2fe; }
        QListWidget::item:alternate { background: #0f172a; }

        /* Inputs details */
        QLineEdit:hover, QDateEdit:hover { border: 1px solid #2f3d5a; }
        QLineEdit:disabled, QDateEdit:disabled { color: #9ca3af; background: #0a0f1a; }

        /* Calendar popup */
        QCalendarWidget { background: #0f172a; border: 1px solid #1f2a44; }
        QCalendarWidget QAbstractItemView:enabled { selection-background-color: #0ea5e9; selection-color: #081321; background: #0b1220; color: #e5e7eb; outline: none; }
        QCalendarWidget QToolButton { color: #e5e7eb; background: transparent; border: none; padding: 6px; }
        QCalendarWidget QToolButton:hover { background: #1f2a44; border-radius: 6px; }
        QCalendarWidget QMenu { background: #0b1220; color: #e5e7eb; border: 1px solid #1f2a44; }
        QCalendarWidget QWidget#qt_calendar_navigationbar { background: #0f172a; }

        /* Scrollbars */
        QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
        QScrollBar::handle:vertical { background: #26334d; min-height: 24px; border-radius: 5px; }
        QScrollBar::handle:vertical:hover { background: #31507a; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
        QScrollBar::handle:horizontal { background: #26334d; min-width: 24px; border-radius: 5px; }
        QScrollBar::handle:horizontal:hover { background: #31507a; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        """
        self.setStyleSheet(stylesheet)

    # ---- Effects ----
    def _apply_shadow(self, widget: QWidget, radius: int = 12, y_offset: int = 4, blur: int = 22, color=(15, 23, 42, 50)):
        try:
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(blur)
            effect.setXOffset(0)
            effect.setYOffset(y_offset)
            from PySide6.QtGui import QColor
            r, g, b, a = color
            effect.setColor(QColor(r, g, b, a))
            widget.setGraphicsEffect(effect)
        except Exception:
            pass

