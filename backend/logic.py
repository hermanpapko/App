import requests
from datetime import date as date_cls

# Uwaga/Note: Open‑Meteo to publiczne API BEZ klucza – nic nie trzeba wklejać.
# Для этого проекта ключ API не требуется: используем публичные эндпоинты.
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherError(Exception):
    pass


def geocode_location(location: str, timeout: float = 8.0):
    if not location:
        raise WeatherError("Pusta lokalizacja.")
    params = {"name": location, "count": 1, "language": "pl", "format": "json"}
    try:
        r = requests.get(GEOCODING_URL, params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            raise WeatherError("Nie znaleziono lokalizacji.")
        res = data["results"][0]
        return {
            "lat": res["latitude"],
            "lon": res["longitude"],
            "name": res.get("name"),
            "country": res.get("country"),
        }
    except requests.RequestException as e:
        raise WeatherError(f"Błąd geokodowania: {e}")


def get_weather(location: str, day: "date|str"):
    """Zwraca prognozę dzienną dla podanej lokalizacji i daty.

    Wynik: dict z polami: date, location_name, tmax, tmin, precipitation, wind_max
    """
    loc = geocode_location(location)
    if isinstance(day, str):
        day_str = day
    elif isinstance(day, date_cls):
        day_str = day.isoformat()
    else:
        raise WeatherError("Nieprawidłowa data.")

    params = {
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            # UWAGA/ВНИМАНИЕ: poprawna nazwa parametru to "wind_speed_10m_max"
            # (nie "windspeed_10m_max"). Błędna nazwa powoduje 400 Bad Request
            # w Open‑Meteo. Zob. https://open-meteo.com/en/docs#api_form
            "wind_speed_10m_max",
        ],
        "timezone": "auto",
        "start_date": day_str,
        "end_date": day_str,
        # Gdy podajemy start_date i end_date, NIE dodajemy forecast_days –
        # te parametry się wykluczają i wywołują błąd 400.
    }
    try:
        r = requests.get(FORECAST_URL, params=params, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        daily = data.get("daily") or {}
        times = (daily.get("time") or [])
        if not times:
            raise WeatherError("Brak danych pogodowych dla tej daty.")
        return {
            "date": times[0],
            "location_name": f"{loc.get('name', '')}, {loc.get('country', '')}".strip(', '),
            "tmax": _first(daily.get("temperature_2m_max")),
            "tmin": _first(daily.get("temperature_2m_min")),
            "precipitation": _first(daily.get("precipitation_sum")),
            "wind_max": _first(daily.get("wind_speed_10m_max")),
        }
    except requests.RequestException as e:
        raise WeatherError(f"Błąd pobierania pogody: {e}")


def _first(arr, default=None):
    try:
        return arr[0]
    except Exception:
        return default
