from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QGraphicsDropShadowEffect,
    QCalendarWidget, QScrollArea, QFrame, QInputDialog, QMenu, QDialog,
    QLineEdit, QComboBox
)
from PySide6.QtCore import QDate, Qt, QEvent
from PySide6.QtCore import QLocale
from backend.database import add_task, list_tasks, toggle_task, delete_task

class AddTaskDialog(QDialog):
    """Диалог добавления задачи, стилизованный под общую концепцию (light/pastel).

    Параметры текста передаются для поддержки i18n.
    """
    def __init__(self, parent=None,
                 title_text: str = "Новая задача",
                 hint_text: str = "Введите текст задачи и нажмите Добавить",
                 placeholder: str = "Например: Купить продукты в 18:00",
                 btn_add_text: str = "Добавить",
                 btn_cancel_text: str = "Отмена"):
        super().__init__(parent)
        self.setObjectName("addDialog")
        self.setModal(True)
        self.setWindowTitle(title_text)

        wrap = QVBoxLayout()
        wrap.setContentsMargins(16, 14, 16, 14)
        wrap.setSpacing(10)

        title = QLabel(title_text)
        title.setObjectName("addTitle")
        hint = QLabel(hint_text)
        hint.setObjectName("addHint")

        self.edit = QLineEdit()
        self.edit.setObjectName("addInput")
        self.edit.setPlaceholderText(placeholder)
        self.edit.setMaxLength(500)

        # Кнопки
        buttons = QHBoxLayout()
        buttons.addStretch()
        self.btn_cancel = QPushButton(btn_cancel_text)
        self.btn_cancel.setObjectName("btnSecondary")
        self.btn_add = QPushButton(btn_add_text)
        self.btn_add.setObjectName("btnPrimary")
        self.btn_add.setEnabled(False)
        buttons.setSpacing(8)
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_add)

        wrap.addWidget(title)
        wrap.addWidget(hint)
        wrap.addWidget(self.edit)
        wrap.addLayout(buttons)
        self.setLayout(wrap)

        # Логика
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_add.clicked.connect(self._on_accept)
        self.edit.textChanged.connect(self._on_text_changed)
        self.edit.returnPressed.connect(self._on_return_pressed)

        # Установка размеров
        self.resize(420, 160)

    def _on_text_changed(self, text: str):
        self.btn_add.setEnabled(bool(text.strip()))

    def _on_return_pressed(self):
        if self.btn_add.isEnabled():
            self._on_accept()

    def _on_accept(self):
        if not self.edit.text().strip():
            return
        self.accept()

    def text(self) -> str:
        return self.edit.text()


class ConfirmDialog(QDialog):
    """Подтверждение действия (удаление) в общем светлом стиле.

    Использование:
        dlg = ConfirmDialog("Удалить задачу", f"Удалить \u00AB{preview}\u00BB? Это действие нельзя отменить.", parent)
        if dlg.exec() == QDialog.Accepted:
            # выполнять удаление
    """
    def __init__(self, title: str, message: str, parent=None,
                 cancel_text: str = "Отмена", ok_text: str = "Удалить"):
        super().__init__(parent)
        self.setObjectName("confirmDialog")
        self.setModal(True)
        self.setWindowTitle(title)

        wrap = QVBoxLayout()
        wrap.setContentsMargins(16, 14, 16, 14)
        wrap.setSpacing(10)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("confirmTitle")
        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setObjectName("confirmMessage")

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.btn_cancel = QPushButton(cancel_text)
        self.btn_cancel.setObjectName("btnSecondary")
        self.btn_delete = QPushButton(ok_text)
        self.btn_delete.setObjectName("btnDanger")
        buttons.setSpacing(8)
        buttons.addWidget(self.btn_cancel)
        buttons.addWidget(self.btn_delete)

        wrap.addWidget(lbl_title)
        wrap.addWidget(lbl_msg)
        wrap.addLayout(buttons)
        self.setLayout(wrap)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_delete.clicked.connect(self.accept)
        self.resize(460, 160)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Meteo Planner PRO")
        self.setMinimumSize(1000, 640)

        # Языки: ru, pl, en
        self.translations = self._build_translations()
        self.lang = "ru"  # язык по умолчанию

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)
        header = self.create_header()
        main_layout.addWidget(header)

        # Главная область: слева календарь и задачи, справа – расписание дня
        content = QHBoxLayout()
        content.setSpacing(16)

        left = self.create_left_column()
        right = self.create_right_column()
        content.addWidget(left, 1)
        content.addWidget(right, 2)

        content_wrap = QWidget()
        content_wrap.setLayout(content)
        main_layout.addWidget(content_wrap, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Режим отображения правой панели: day | week | month
        self.view_mode = "day"

        # Применяем светлую, минималистичную тему с пастельными акцентами
        self.apply_styles()

        # Применить язык к уже созданным виджетам
        self.set_language(self.lang, initial=True)

        # Initial load
        self.calendar.setSelectedDate(QDate.currentDate())
        # Контекстное меню для списка задач + обработка клавиши Delete
        self.tasks_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tasks_list.customContextMenuRequested.connect(self.show_tasks_context_menu)
        self.tasks_list.installEventFilter(self)
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

        # Переключатели Day / Week / Month (теперь рабочие)
        self.btn_day = QPushButton("Day")
        self.btn_week = QPushButton("Week")
        self.btn_month = QPushButton("Month")
        for b in (self.btn_day, self.btn_week, self.btn_month):
            b.setCheckable(True)
            b.setObjectName("segButton")
            layout.addWidget(b)
        self.btn_day.setChecked(True)

        # Селектор языка
        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("langCombo")
        self.lang_combo.addItem("Русский", userData="ru")
        self.lang_combo.addItem("Polski", userData="pl")
        self.lang_combo.addItem("English", userData="en")
        # Выставим текущий
        self.lang_combo.setCurrentIndex(0)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        layout.addWidget(self.lang_combo)

        # Wiring: переключение режимов
        self.btn_day.clicked.connect(lambda: self.set_view_mode("day"))
        self.btn_week.clicked.connect(lambda: self.set_view_mode("week"))
        self.btn_month.clicked.connect(lambda: self.set_view_mode("month"))

        # Профиль (заглушка)
        # self.btn_profile = QPushButton("🙂")
        # self.btn_profile.setObjectName("profileButton")
        # layout.addWidget(self.btn_profile)

        header.setLayout(layout)
        # Subtle shadow for depth
        self._apply_shadow(header, radius=16, y_offset=3, blur=24, color=(83, 56, 206, 60))
        return header

    def create_left_column(self):
        box = QWidget()
        box.setObjectName("leftColumn")
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(12)

        # Календарь месяца
        self.calendar = QCalendarWidget()
        self.calendar.setObjectName("monthCalendar")
        self.calendar.selectionChanged.connect(self.on_calendar_changed)

        # Список задач (с чекбоксами)
        tasks_card = QWidget()
        tasks_card.setObjectName("tasksPanel")
        tv = QVBoxLayout()
        tv.setContentsMargins(16, 12, 16, 12)
        tv.setSpacing(10)

        header = QHBoxLayout()
        lbl = QLabel("Задачи и заметки")
        lbl.setObjectName("sectionTitle")
        header.addWidget(lbl)
        header.addStretch()
        # Кнопка удаления (видимая), выключена по умолчанию
        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.setEnabled(False)
        self.btn_delete.setToolTip("Удалить выбранную задачу")
        self.btn_delete.clicked.connect(self.delete_task_clicked)
        header.addWidget(self.btn_delete)
        tv.addLayout(header)

        self.tasks_list = QListWidget()
        self.tasks_list.setAlternatingRowColors(True)
        self.tasks_list.itemChanged.connect(self.on_task_item_changed)
        # Обновлять доступность кнопки удаления при смене выбора
        self.tasks_list.itemSelectionChanged.connect(self.update_delete_enabled)
        tv.addWidget(self.tasks_list)

        tasks_card.setLayout(tv)
        self._apply_shadow(tasks_card, blur=22, y_offset=3, color=(0,0,0,40))

        v.addWidget(self.calendar)
        v.addWidget(tasks_card, 1)
        box.setLayout(v)
        return box

    def create_right_column(self):
        box = QWidget()
        box.setObjectName("rightColumn")
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(12)

        # Заголовок и описание дня
        head = QWidget()
        head.setObjectName("dayHeader")
        hl = QHBoxLayout()
        hl.setContentsMargins(16, 12, 16, 12)
        title = QLabel("Расписание дня")
        title.setObjectName("sectionTitle")
        self.lbl_selected_date = QLabel("")
        self.lbl_selected_date.setObjectName("muted")
        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(self.lbl_selected_date)
        head.setLayout(hl)

        # Прокручиваемая зона с карточками событий (используем задачи как события)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dayScroll")
        self.day_container = QWidget()
        self.day_container.setObjectName("dayContainer")
        self.day_layout = QVBoxLayout()
        self.day_layout.setContentsMargins(16, 12, 16, 12)
        self.day_layout.setSpacing(10)
        self.day_container.setLayout(self.day_layout)
        scroll.setWidget(self.day_container)

        # Плавающая круглая кнопка «+»
        self.fab_add = QPushButton("+")
        self.fab_add.setObjectName("fabAdd")
        self.fab_add.setToolTip("Добавить задачу")
        self.fab_add.clicked.connect(self.add_task_fab)

        v.addWidget(head)
        v.addWidget(scroll, 1)

        # Контейнер для позиционирования FAB справа снизу
        wrap = QFrame()
        wf = QVBoxLayout()
        wf.setContentsMargins(0, 0, 0, 0)
        wf.addWidget(self.fab_add, 0, Qt.AlignRight | Qt.AlignBottom)
        wrap.setLayout(wf)
        v.addWidget(wrap, 0, Qt.AlignRight | Qt.AlignBottom)

        box.setLayout(v)
        return box

    # (устаревшее) create_tasks_panel удалено — задачи теперь в левой колонке и FAB добавления

    # ---- Actions ----
    def refresh_all(self):
        self.load_tasks()
        self.populate_right_view()

    def current_date_qdate(self):
        return self.calendar.selectedDate()

    def current_date_str(self):
        return self.current_date_qdate().toString("yyyy-MM-dd")

    def on_calendar_changed(self):
        self.refresh_all()

    def load_tasks(self):
        # Во время заполнения временно блокируем сигналы, чтобы не вызывать on_task_item_changed
        self.tasks_list.blockSignals(True)
        self.tasks_list.clear()
        # В новой концепции локация не используется — грузим по дате
        tasks = list_tasks(self.current_date_str(), None)
        for t in tasks:
            item = QListWidgetItem(t["text"])
            item.setData(Qt.UserRole, t["id"])  # id
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            item.setCheckState(Qt.Checked if t["done"] else Qt.Unchecked)
            self.tasks_list.addItem(item)
        self.tasks_list.blockSignals(False)
        self.update_delete_enabled()

    def add_task_fab(self):
        # Пользовательский диалог в едином стиле вместо стандартного QInputDialog
        # Локализованные тексты для диалога
        t = self.t
        dlg = AddTaskDialog(
            self,
            title_text=t("add_title"),
            hint_text=t("add_hint"),
            placeholder=t("add_placeholder"),
            btn_add_text=t("add_confirm"),
            btn_cancel_text=t("cancel"),
        )
        if dlg.exec() == QDialog.Accepted:
            txt = dlg.text().strip()
            if txt:
                add_task(self.current_date_str(), txt, None)
                self.refresh_all()

    def _selected_task_id(self):
        item = self.tasks_list.currentItem()
        if not item:
            return None
        return item.data(Qt.UserRole)

    def toggle_task_clicked(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        toggle_task(int(tid))
        self.refresh_all()

    def delete_task_clicked(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        # Подтверждение удаления (кастомный диалог в общем стиле)
        item = self.tasks_list.currentItem()
        text_preview = item.text() if item else self.t("this_task")
        dlg = ConfirmDialog(
            self.t("delete_title"),
            self.t("delete_message").format(task=text_preview),
            self,
            cancel_text=self.t("cancel"),
            ok_text=self.t("delete"),
        )
        if dlg.exec() != QDialog.Accepted:
            return
        delete_task(int(tid))
        self.refresh_all()

    def update_delete_enabled(self):
        has_selection = self.tasks_list.currentItem() is not None
        if hasattr(self, "btn_delete"):
            self.btn_delete.setEnabled(has_selection)

    def show_tasks_context_menu(self, pos):
        # Выбрать элемент под курсором (если есть)
        item = self.tasks_list.itemAt(pos)
        if item is not None:
            self.tasks_list.setCurrentItem(item)
        menu = QMenu(self)
        act_del = menu.addAction(self.t("delete"))
        # Отключить, если ничего не выбрано
        act_del.setEnabled(self.tasks_list.currentItem() is not None)
        action = menu.exec(self.tasks_list.mapToGlobal(pos))
        if action == act_del:
            self.delete_task_clicked()

    def eventFilter(self, obj, event):
        if obj is self.tasks_list and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                # Удаление выбранной задачи по Delete/Backspace
                if self._selected_task_id() is not None:
                    self.delete_task_clicked()
                    return True
        return super().eventFilter(obj, event)

    def on_task_item_changed(self, item: QListWidgetItem):
        # Переключение чекбокса меняет состояние done
        tid = item.data(Qt.UserRole)
        if tid is None:
            return
        # Чтобы избежать рекурсии/лишних апдейтов, просто дергаем toggle,
        # который инвертирует состояние в БД до нужного.
        toggle_task(int(tid))
        # Обновим правую колонку (карточки)
        self.populate_right_view()

    # ---- View mode switching ----
    def set_view_mode(self, mode: str):
        if mode not in ("day", "week", "month"):
            return
        self.view_mode = mode
        # Эксклюзивная отметка кнопок
        self.btn_day.blockSignals(True)
        self.btn_week.blockSignals(True)
        self.btn_month.blockSignals(True)
        self.btn_day.setChecked(mode == "day")
        self.btn_week.setChecked(mode == "week")
        self.btn_month.setChecked(mode == "month")
        self.btn_day.blockSignals(False)
        self.btn_week.blockSignals(False)
        self.btn_month.blockSignals(False)
        # Перерисовать правую панель
        self.populate_right_view()

    def populate_right_view(self):
        if self.view_mode == "day":
            self.populate_day_view()
        elif self.view_mode == "week":
            self.populate_week_view()
        else:
            self.populate_month_view()

    def populate_day_view(self):
        # Очистить текущие карточки
        while self.day_layout.count():
            item = self.day_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        # Заголовок даты
        # Локализованное отображение даты
        # Локализуем названия дней/месяцев через QLocale
        self.lbl_selected_date.setText(QLocale().toString(self.current_date_qdate(), "ddd, d MMM yyyy"))
        # Загрузить задачи и отрисовать как карточки событий с пастельными маркерами
        tasks = list_tasks(self.current_date_str(), None)
        if not tasks:
            empty = QLabel(self.t("empty_day"))
            empty.setObjectName("muted")
            self.day_layout.addWidget(empty)
            return
        colors = ["#FBCFE8", "#BBF7D0", "#FEF3C7", "#BFDBFE", "#E9D5FF"]
        for idx, t in enumerate(tasks):
            card = QWidget()
            card.setObjectName("eventCard")
            hl = QHBoxLayout()
            hl.setContentsMargins(12, 10, 12, 10)
            hl.setSpacing(10)

            marker = QFrame()
            marker.setFixedWidth(6)
            marker.setObjectName("eventMarker")
            marker.setStyleSheet(f"background: {colors[idx % len(colors)]}; border-radius: 3px;")

            text = QLabel(t["text"])
            if t["done"]:
                f = text.font()
                f.setStrikeOut(True)
                text.setFont(f)
                text.setStyleSheet("color: #9CA3AF;")

            hl.addWidget(marker)
            hl.addWidget(text, 1)

            card.setLayout(hl)
            card.setProperty("done", t["done"])  # для стилизации, если понадобится
            self._apply_shadow(card, blur=18, y_offset=2, color=(0,0,0,30))
            self.day_layout.addWidget(card)

    def _clear_right_cards(self):
        while self.day_layout.count():
            item = self.day_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _add_group_header(self, date_q: QDate):
        header = QLabel(QLocale().toString(date_q, "ddd, d MMM"))
        header.setObjectName("muted")
        # Небольшие отступы сверху
        wrap = QWidget()
        v = QVBoxLayout()
        v.setContentsMargins(4, 8, 4, 0)
        v.addWidget(header)
        wrap.setLayout(v)
        self.day_layout.addWidget(wrap)

    def _add_task_card(self, text: str, done: bool, color: str):
        card = QWidget()
        card.setObjectName("eventCard")
        hl = QHBoxLayout()
        hl.setContentsMargins(12, 10, 12, 10)
        hl.setSpacing(10)
        marker = QFrame()
        marker.setFixedWidth(6)
        marker.setObjectName("eventMarker")
        marker.setStyleSheet(f"background: {color}; border-radius: 3px;")
        lbl = QLabel(text)
        if done:
            f = lbl.font()
            f.setStrikeOut(True)
            lbl.setFont(f)
            lbl.setStyleSheet("color: #9CA3AF;")
        hl.addWidget(marker)
        hl.addWidget(lbl, 1)
        card.setLayout(hl)
        card.setProperty("done", done)
        self._apply_shadow(card, blur=18, y_offset=2, color=(0,0,0,30))
        self.day_layout.addWidget(card)

    def populate_week_view(self):
        self._clear_right_cards()
        current = self.current_date_qdate()
        # QDate.dayOfWeek(): 1=Mon .. 7=Sun
        start = current.addDays(1 - current.dayOfWeek())
        end = start.addDays(6)
        self.lbl_selected_date.setText(self.t("week_range").format(start=QLocale().toString(start, 'd MMM'), end=QLocale().toString(end, 'd MMM yyyy')))
        colors = ["#FBCFE8", "#BBF7D0", "#FEF3C7", "#BFDBFE", "#E9D5FF"]
        any_tasks = False
        for i in range(7):
            d = start.addDays(i)
            ds = d.toString("yyyy-MM-dd")
            tasks = list_tasks(ds, None)
            if not tasks:
                continue
            any_tasks = True
            self._add_group_header(d)
            for idx, t in enumerate(tasks):
                self._add_task_card(t["text"], t["done"], colors[idx % len(colors)])
        if not any_tasks:
            empty = QLabel(self.t("empty_week"))
            empty.setObjectName("muted")
            self.day_layout.addWidget(empty)

    def populate_month_view(self):
        self._clear_right_cards()
        current = self.current_date_qdate()
        first = QDate(current.year(), current.month(), 1)
        last = first.addMonths(1).addDays(-1)
        self.lbl_selected_date.setText(QLocale().toString(first, "MMMM yyyy"))
        colors = ["#FBCFE8", "#BBF7D0", "#FEF3C7", "#BFDBFE", "#E9D5FF"]
        any_tasks = False
        d = first
        while d <= last:
            ds = d.toString("yyyy-MM-dd")
            tasks = list_tasks(ds, None)
            if tasks:
                any_tasks = True
                self._add_group_header(d)
                for idx, t in enumerate(tasks):
                    self._add_task_card(t["text"], t["done"], colors[idx % len(colors)])
            d = d.addDays(1)
        if not any_tasks:
            empty = QLabel(self.t("empty_month"))
            empty.setObjectName("muted")
            self.day_layout.addWidget(empty)

    # ---- Styles ----
    def apply_styles(self):
        stylesheet = """
        /* Base: светлая, минималистичная палитра */
        QWidget { font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, Arial; font-size: 14px; color: #1F2937; background: #F8FAFC; }

        /* Header */
        #headerBar { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; }
        #headerBar QLabel#appTitle { color: #111827; font-size: 20px; font-weight: 700; letter-spacing: 0.2px; }
        QPushButton#profileButton { background: #F3F4F6; border: 1px solid #E5E7EB; color: #6B7280; border-radius: 18px; padding: 6px 10px; }
        QPushButton#profileButton:hover { background: #E5E7EB; }

        /* Segmented control */
        QPushButton#segButton { background: #F3F4F6; border: 1px solid #E5E7EB; color: #4B5563; border-radius: 8px; padding: 6px 12px; }
        QPushButton#segButton:hover { background: #EAECEF; }
        QPushButton#segButton:checked { background: #EEF2FF; color: #4F46E5; border-color: #C7D2FE; }

        /* Language Combo — improved pastel/rounded design */
        QComboBox#langCombo {
            background: #FFFFFF;
            border: 1.5px solid #D8DAE0;
            color: #374151;
            border-radius: 12px;
            padding: 8px 40px 8px 14px;
            min-width: 150px;
        }

        QComboBox#langCombo:hover {
            background: #F4F6FB;
            border-color: #C7D2FE;
        }

        QComboBox#langCombo:focus {
            border-color: #A5B4FC;
        }

        QComboBox#langCombo:disabled {
            color: #9CA3AF;
            background: #F3F4F6;
        }

        /* Dropdown arrow container */
        QComboBox#langCombo::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 32px;
            border-left: 1px solid #D8DAE0;
            background: #F4F6FB;
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
        }

        QComboBox#langCombo::drop-down:hover {
            background: #ECEFFF;
            border-left: 1px solid #C7D2FE;
        }

        /* Arrow icons */
        QComboBox#langCombo::down-arrow {
            image: url(ui/assets/chevron-down.svg);
            width: 16px;
            height: 16px;
            margin-right: 8px;
        }

        QComboBox#langCombo::down-arrow:on {
            image: url(ui/assets/chevron-up.svg);
            width: 16px;
            height: 16px;
            margin-right: 8px;
        }

        /* Opened state */
        QComboBox#langCombo:on {
            border-color: #A5B4FC;
        }

        QComboBox#langCombo::drop-down:on {
            background: #EEF2FF;
            border-left: 1px solid #A5B4FC;
        }

        /* Popup list */
        QComboBox#langCombo QAbstractItemView {
            background: #FFFFFF;
            border: 1.5px solid #D8DAE0;
            border-radius: 12px;
            outline: none;
            padding: 6px 0;
        }

        QComboBox#langCombo QAbstractItemView::item {
            padding: 10px 14px;
            color: #111827;
            border-radius: 6px;
        }

        QComboBox#langCombo QAbstractItemView::item:hover {
            background: #F4F6FB;
        }

        QComboBox#langCombo QAbstractItemView::item:selected {
            background: #EEF2FF;
            color: #4F46E5;
        }

        /* Left column */
        #leftColumn { }
        QCalendarWidget#monthCalendar { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; }
        QCalendarWidget#monthCalendar QWidget#qt_calendar_navigationbar { background: #FFFFFF; }
        QCalendarWidget#monthCalendar QToolButton { color: #374151; background: transparent; border: none; padding: 6px; }
        QCalendarWidget#monthCalendar QToolButton:hover { background: #F3F4F6; border-radius: 6px; }
        QCalendarWidget#monthCalendar QAbstractItemView:enabled { selection-background-color: #EDE9FE; selection-color: #4F46E5; background: #FFFFFF; color: #111827; outline: none; }

        #tasksPanel { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; }
        #tasksPanel QLabel#sectionTitle { font-weight: 700; color: #111827; }
        QListWidget { border: 1px solid #E5E7EB; border-radius: 10px; padding: 6px; background: #FFFFFF; }
        QListWidget::item { padding: 8px 10px; }
        QListWidget::item:hover { background: #F9FAFB; }
        QListWidget::item:selected { background: #EEF2FF; color: #4F46E5; }
        QListWidget::item:alternate { background: #FAFAFA; }

        /* Явный квадратный чекбокс у задач */
        QListWidget::indicator {
            width: 18px;
            height: 18px;
            margin-right: 8px; /* отступ от текста */
        }
        QListWidget::indicator:unchecked {
            border: 2px solid #D1D5DB; /* явная рамка */
            background: #FFFFFF;       /* белый фон */
            border-radius: 3px;        /* почти квадратный, без сильного скругления */
        }
        QListWidget::indicator:unchecked:hover {
            border-color: #9CA3AF;
            background: #F9FAFB;
        }
        QListWidget::indicator:checked {
            border: 2px solid #8B5CF6;
            background: #8B5CF6;      /* заливка акцентом; галочка будет контрастной */
            border-radius: 3px;
        }
        QListWidget::indicator:checked:hover {
            background: #7C3AED;
            border-color: #7C3AED;
        }

        /* Right column */
        #dayHeader { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; }
        QLabel#sectionTitle { font-weight: 700; color: #111827; }
        QLabel#muted { color: #6B7280; }
        #dayScroll { border: 1px solid #E5E7EB; border-radius: 12px; background: #FFFFFF; }
        #dayContainer { background: transparent; }
        #eventCard, QWidget#eventCard { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; }

        /* FAB */
        QPushButton#fabAdd { background: #8B5CF6; color: #FFFFFF; border: none; border-radius: 22px; font-size: 20px; font-weight: 700; padding: 8px 14px; }
        QPushButton#fabAdd:hover { background: #7C3AED; }
        QPushButton#fabAdd:pressed { background: #6D28D9; }

        /* Add Task Dialog */
        QDialog#addDialog { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; }
        QDialog#addDialog QLabel#addTitle { font-size: 16px; font-weight: 700; color: #111827; }
        QDialog#addDialog QLabel#addHint { color: #6B7280; }
        QLineEdit#addInput { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 8px 10px; }
        QLineEdit#addInput:focus { border-color: #C7D2FE; box-shadow: 0 0 0 3px rgba(99,102,241,0.15); }
        QPushButton#btnPrimary { background: #8B5CF6; color: #FFFFFF; border: none; border-radius: 10px; padding: 8px 14px; font-weight: 600; }
        QPushButton#btnPrimary:hover { background: #7C3AED; }
        QPushButton#btnPrimary:pressed { background: #6D28D9; }
        QPushButton#btnPrimary:disabled { background: #E5E7EB; color: #9CA3AF; }
        QPushButton#btnSecondary { background: #F3F4F6; color: #374151; border: 1px solid #E5E7EB; border-radius: 10px; padding: 8px 14px; }
        QPushButton#btnSecondary:hover { background: #EAECEF; }

        /* Confirm Dialog (удаление) */
        QDialog#confirmDialog { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; }
        QDialog#confirmDialog QLabel#confirmTitle { font-size: 16px; font-weight: 700; color: #111827; }
        QDialog#confirmDialog QLabel#confirmMessage { color: #374151; }
        QPushButton#btnDanger { background: #EF4444; color: #FFFFFF; border: none; border-radius: 10px; padding: 8px 14px; font-weight: 600; }
        QPushButton#btnDanger:hover { background: #DC2626; }
        QPushButton#btnDanger:pressed { background: #B91C1C; }
        
        /* Scrollbars (light) */
        QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
        QScrollBar::handle:vertical { background: #E5E7EB; min-height: 24px; border-radius: 5px; }
        QScrollBar::handle:vertical:hover { background: #D1D5DB; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
        QScrollBar::handle:horizontal { background: #E5E7EB; min-width: 24px; border-radius: 5px; }
        QScrollBar::handle:horizontal:hover { background: #D1D5DB; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        """
        self.setStyleSheet(stylesheet)

    # ---- Effects ----
    def _apply_shadow(self, widget: QWidget, radius: int = 12, y_offset: int = 4, blur: int = 22, color=(0, 0, 0, 40)):
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

    # ---- I18N ----
    def _build_translations(self):
        return {
            "ru": {
                "seg_day": "День",
                "seg_week": "Неделя",
                "seg_month": "Месяц",
                "tasks_title": "Задачи и заметки",
                "delete": "Удалить",
                "delete_tooltip": "Удалить выбранную задачу",
                "schedule_title": "Расписание дня",
                "fab_tooltip": "Добавить задачу",
                "empty_day": "На этот день нет событий. Нажмите + чтобы добавить.",
                "empty_week": "На эту неделю нет событий. Нажмите + чтобы добавить.",
                "empty_month": "В этом месяце пока нет событий. Нажмите + чтобы добавить.",
                "delete_title": "Удалить задачу",
                "delete_message": "Удалить «{task}»? Это действие нельзя отменить.",
                "cancel": "Отмена",
                "this_task": "эту задачу",
                "add_title": "Новая задача",
                "add_hint": "Введите текст задачи и нажмите Добавить",
                "add_placeholder": "Например: Купить продукты в 18:00",
                "add_confirm": "Добавить",
                "week_range": "Неделя: {start} – {end}",
            },
            "pl": {
                "seg_day": "Dzień",
                "seg_week": "Tydzień",
                "seg_month": "Miesiąc",
                "tasks_title": "Zadania i notatki",
                "delete": "Usuń",
                "delete_tooltip": "Usuń wybrane zadanie",
                "schedule_title": "Plan dnia",
                "fab_tooltip": "Dodaj zadanie",
                "empty_day": "Brak wydarzeń na ten dzień. Kliknij + aby dodać.",
                "empty_week": "Brak wydarzeń w tym tygodniu. Kliknij + aby dodać.",
                "empty_month": "W tym miesiącu brak wydarzeń. Kliknij + aby dodać.",
                "delete_title": "Usunąć zadanie",
                "delete_message": "Usunąć \u00AB{task}\u00BB? Tej operacji nie można cofnąć.",
                "cancel": "Anuluj",
                "this_task": "to zadanie",
                "add_title": "Nowe zadanie",
                "add_hint": "Wpisz treść zadania i kliknij Dodaj",
                "add_placeholder": "Np.: Kupić produkty o 18:00",
                "add_confirm": "Dodaj",
                "week_range": "Tydzień: {start} – {end}",
            },
            "en": {
                "seg_day": "Day",
                "seg_week": "Week",
                "seg_month": "Month",
                "tasks_title": "Tasks & Notes",
                "delete": "Delete",
                "delete_tooltip": "Delete selected task",
                "schedule_title": "Day schedule",
                "fab_tooltip": "Add task",
                "empty_day": "No events for this day. Click + to add.",
                "empty_week": "No events this week. Click + to add.",
                "empty_month": "No events this month yet. Click + to add.",
                "delete_title": "Delete task",
                "delete_message": "Delete \u00AB{task}\u00BB? This action cannot be undone.",
                "cancel": "Cancel",
                "this_task": "this task",
                "add_title": "New task",
                "add_hint": "Enter task text and click Add",
                "add_placeholder": "E.g.: Buy groceries at 6 PM",
                "add_confirm": "Add",
                "week_range": "Week: {start} – {end}",
            },
        }

    def t(self, key: str) -> str:
        return self.translations.get(self.lang, {}).get(key, key)

    def _on_lang_changed(self, idx: int):
        lang = self.lang_combo.currentData() or "ru"
        self.set_language(lang)

    def set_language(self, lang: str, initial: bool = False):
        if lang not in ("ru", "pl", "en"):
            lang = "ru"
        self.lang = lang
        # Установить локаль Qt для форматирования дат и календаря
        locale_map = {
            "ru": QLocale(QLocale.Russian, QLocale.Russia),
            "pl": QLocale(QLocale.Polish, QLocale.Poland),
            "en": QLocale(QLocale.English, QLocale.UnitedStates),
        }
        ql = locale_map[lang]
        QLocale.setDefault(ql)
        self.calendar.setLocale(ql)
        # Перепривязать все строки интерфейса
        self._apply_language_to_widgets()
        # Перерисовать правую панель (для пустых сообщений и заголовков)
        if not initial:
            self.refresh_all()

    def _apply_language_to_widgets(self):
        # Переключатели режима
        self.btn_day.setText(self.t("seg_day"))
        self.btn_week.setText(self.t("seg_week"))
        self.btn_month.setText(self.t("seg_month"))
        # Заголовки и подсказки
        # Левый столбец: заголовок и кнопка удаления
        # Найдём метку заголовка в панели задач
        # (первая QLabel в layout заголовка tasks_panel)
        # Мы сохранили объект только для кнопки; создадим новое имя для метки
        # Для простоты пройдемся по детям tasksPanel
        try:
            tasks_panel = None
            for ch in self.findChildren(QWidget):
                if ch.objectName() == "tasksPanel":
                    tasks_panel = ch
                    break
            if tasks_panel:
                lbls = tasks_panel.findChildren(QLabel, "sectionTitle")
                if lbls:
                    lbls[0].setText(self.t("tasks_title"))
        except Exception:
            pass
        self.btn_delete.setText(self.t("delete"))
        self.btn_delete.setToolTip(self.t("delete_tooltip"))
        # Правая колонка заголовок
        try:
            right_title = None
            # dayHeader has QLabel#sectionTitle
            head = self.findChild(QWidget, "dayHeader")
            if head:
                lbls = head.findChildren(QLabel, "sectionTitle")
                if lbls:
                    lbls[0].setText(self.t("schedule_title"))
        except Exception:
            pass
        # FAB
        self.fab_add.setToolTip(self.t("fab_tooltip"))

