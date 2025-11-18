# Meteo Planner PRO

Desktopowa aplikacja (PySide6) z widokiem kalendarza i planera задач w nowoczesnym, jasnym (light) i minimalistycznym дизайне.

Funkcje:
- Kalendarz miesiąca po lewej i список задач z чекбоксами.
- Расписание wybranego dnia po prawej: задачи отображаются w виде карточек z пастельными маркерами.
- Быстрое добавление задач через плавающую круглую кнопку «+».
 - Удаление задач: через видимую кнопку «🗑 Удалить» над списком, по правому клику (контекстное меню «Удалить») или клавишей Delete/Backspace — с стильным подтверждением.

Design / Wygląd:
- Jasny, czysty интерфейс na białym tle, pastelowe akcenty i miękkie cienie.
- Верхняя панель с переключателями Day / Week / Month — теперь рабочими: переключают правую колонку между дневным, недельным и месячным видами; активный режим подсвечен.
- Календарь месяца — лёгкая типографика, аккуратная подсветка выбранного дня сиреневым тоном.

Języki / Языки / Languages:
- Aplikacja wspiera 3 języki: Polski, Русский i English.
- Переключатель языка находится в правой части верхней панели (combo: Polski / Русский / English).
- Date names in the calendar and headers are localized via system QLocale.


Wymagania
- Python 3.10+
- PostgreSQL uruchomiony lokalnie (domyślnie: dbname=app_db, user=herman, host=localhost, port=5432)


Instalacja
1. Utwórz i aktywuj środowisko wirtualne (opcjonalnie):
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # lub .venv\Scripts\activate  # Windows

2. Zainstaluj zależności:
   pip install -r requirements.txt

3. Skonfiguruj bazę danych:
   - Utwórz bazę danych app_db i użytkownika herman, lub dostosuj ustawienia w backend/database.py -> DB_CONFIG.
   - Aplikacja sama utworzy tabelę users i tasks przy pierwszym uruchomieniu.

4. Uruchom aplikację:
   python main.py


Uwagi techniczne
- Dane zadań są przechowywane w tabeli tasks (task_date, text, location, done). W текущем дизайне lokalizacja nie jest wykorzystywana (można pozostawić puste).
- Переключение даты осуществляется через календарь; список слева показывает задачи выбранного дня. Кнопки Day/Week/Month управляют тем, как отображаются задачи справа: за день, неделю (Пн‑Вс) или месяц (группами по датам).
 - Удаление: выделите задачу и нажмите кнопку «🗑 Удалить» над списком. Также работает правый клик → «Удалить» или клавиша Delete/Backspace. Откроется аккуратный диалог подтверждения в общем светлом стиле.

Struktura projektu
- main.py – start aplikacji
- ui/main_window.py – interfejs użytkownika (PySide6, светлая тема) + i18n (PL/RU/EN)
- backend/database.py – warstwa dostępu do PostgreSQL (tworzenie tabel, CRUD zadań)
- backend/logic.py – (opcjonalnie) wcześniejsza логика погоды; не используется в текущем дизайне


Uwagi dot. motywów (PL/RU)
- PL: Aplikacja używa jasnego, minimalistycznego motywu. Styl zaimplementowany w apply_styles() (ui/main_window.py). Białe karty, pastelowe markery, delikatne cienie.
- RU: Приложение использует светлую минималистичную тему. Стиль в apply_styles() (ui/main_window.py): белые карточки, пастельные маркеры, мягкие тени.


FAQ (RU)
- База данных: необходимо настроить доступ к PostgreSQL.
  - Вариант 1: Создайте БД и пользователя как в примере:
    - База: app_db
    - Пользователь: herman (любой пароль/без пароля по вашему окружению)
    - Хост: localhost, Порт: 5432
  - Вариант 2: Измените настройки в backend/database.py -> словарь DB_CONFIG на свои значения:
    - dbname, user, password, host, port
  - Пример команд (Linux/macOS) для быстрой настройки:
    1) sudo -u postgres createuser -P herman   # задать пароль
    2) sudo -u postgres createdb app_db -O herman
    3) При необходимости выдать права: GRANT ALL PRIVILEGES ON DATABASE app_db TO herman;

- Погода: в текущем дизайне погодные данные не отображаются. Модуль backend/logic.py оставлен для совместимости, но UI его не использует.