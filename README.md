# Meteo Planner PRO

Prosta aplikacja desktopowa (PySide6) łącząca plan dnia z prognozą pogody.

Funkcje:
- Wybór lokalizacji (geokodowanie Open‑Meteo, bez klucza API)
- Wybór daty i podgląd prognozy dziennej: Tmax/Tmin, opady, wiatr
- Lista zadań dla wybranej daty i lokalizacji: dodawanie, oznaczanie ukończonych, usuwanie

Design / Wygląd:
- Nowoczesny wygląd z zaokrąglonymi kartami, delikatnymi cieniami i spójną kolorystyką
- Tylko ciemny motyw (dark) — dopracowane szczegóły: focus/hover, scrollbary, kalendarz
- Czytelne stany przycisków (primary/secondary/danger) i podświetlenia elementów


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
- Prognoza pogody korzysta z Open‑Meteo (https://open-meteo.com). Nie wymaga klucza.
- Geokodowanie lokalizacji: endpoint geocoding-api.open-meteo.com.
- Operacje sieciowe mają podstawową obsługę błędów i time‑out.
- Dane zadań są przechowywane w tabeli tasks (task_date, text, location, done).

Struktura projektu
- main.py – start aplikacji
- ui/main_window.py – interfejs użytkownika (PySide6)
- backend/logic.py – logika pogody (geokodowanie + prognoza)
- backend/database.py – warstwa dostępu do PostgreSQL (tworzenie tabel, CRUD zadań)


Uwagi dot. motywów (PL/RU)
- PL: Aplikacja używa wyłącznie ciemnego motywu. Styl zaimplementowany w apply_styles() (ui/main_window.py). Karty mają subtelne cienie (QGraphicsDropShadowEffect); dopracowano kalendarz, listy oraz scrollbary w trybie dark.
- RU: Приложение использует только тёмную тему. Стиль задан в apply_styles() (ui/main_window.py). Карточки с аккуратными тенями; улучшены календарь, списки и скроллбары для тёмного режима.


FAQ (RU): Где взять API и что куда вставить?
- Погода: приложение использует публичное API Open‑Meteo, оно НЕ ТРЕБУЕТ ключа. Ничего никуда вставлять не нужно.
  - Эндпоинты: 
    - Геокодирование: https://geocoding-api.open-meteo.com/v1/search
    - Прогноз: https://api.open-meteo.com/v1/forecast
  - Места в коде: backend/logic.py (константы GEOCODING_URL и FORECAST_URL). Комментарии в файле отмечают, что ключ не нужен.

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

- Что делать, если нужен другой провайдер погоды с ключом API?
  - Замените логику в backend/logic.py: 
    - Добавьте ключ как параметр запроса (params={"apikey": "ВАШ_КЛЮЧ", ...}) или как заголовок (headers={"Authorization": "Bearer ВАШ_КЛЮЧ"}).
    - Поменяйте URL на эндпоинты вашего провайдера (вместо FORECAST_URL/GEOCODING_URL).
    - Сохраните формат возвращаемого словаря в get_weather (date, location_name, tmax, tmin, precipitation, wind_max), чтобы UI продолжал работать без изменений.
  - Комментарии в backend/logic.py рядом с URL подскажут, где это делать.