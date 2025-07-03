import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from core.models import City, WeatherData, WeatherAlert, WeatherCondition

class Command(BaseCommand):
    help = "Fetch current weather and forecast for all cities, store data and create alerts if rain expected next hour."

    def handle(self, *args, **options):
        api_key = getattr(settings, 'WEATHER_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR("WEATHER_API_KEY not set in settings.py"))
            return

        base_url = 'http://api.weatherapi.com/v1/forecast.json'

        cities = City.objects.all()
        if not cities:
            self.stdout.write(self.style.WARNING("No cities found. Please add some cities first."))
            return

        weather_count = 0
        alert_count = 0

        for city in cities:
            params = {
                'key': api_key,
                'q': city.name,
                'hours': 2,
                'aqi': 'no',
                'alerts': 'no',
            }
            try:
                response = requests.get(base_url, params=params, timeout=10)
                data = response.json()

                if 'error' in data:
                    self.stdout.write(self.style.WARNING(
                        f"Could not fetch weather for {city.name}: {data['error']['message']}"
                    ))
                    continue

                current = data['current']
                forecast_hours = data['forecast']['forecastday'][0]['hour']

                # Получаем или создаём WeatherCondition
                cond_data = current['condition']
                condition, _ = WeatherCondition.objects.get_or_create(
                    code=cond_data.get('code', 0),
                    defaults={'text': cond_data.get('text', ''), 'icon_url': cond_data.get('icon', '')}
                )

                # Записываем текущую погоду
                WeatherData.objects.create(
                    city=city,
                    last_updated=timezone.now(),
                    temp_c=current['temp_c'],
                    temp_f=current['temp_f'],
                    is_day=current['is_day'],
                    condition=condition,
                    wind_mph=current['wind_mph'],
                    wind_kph=current['wind_kph'],
                    wind_degree=current['wind_degree'],
                    wind_dir=current['wind_dir'],
                    pressure_mb=current['pressure_mb'],
                    pressure_in=current['pressure_in'],
                    precip_mm=current['precip_mm'],
                    precip_in=current['precip_in'],
                    humidity=current['humidity'],
                    cloud=current['cloud'],
                    feelslike_c=current['feelslike_c'],
                    feelslike_f=current['feelslike_f'],
                    windchill_c=current.get('windchill_c', current['feelslike_c']),
                    windchill_f=current.get('windchill_f', current['feelslike_f']),
                    heatindex_c=current.get('heatindex_c', current['feelslike_c']),
                    heatindex_f=current.get('heatindex_f', current['feelslike_f']),
                    dewpoint_c=current.get('dewpoint_c', 0),
                    dewpoint_f=current.get('dewpoint_f', 0),
                    vis_km=current['vis_km'],
                    vis_miles=current['vis_miles'],
                    uv=current['uv'],
                    gust_mph=current['gust_mph'],
                    gust_kph=current['gust_kph'],
                )
                weather_count += 1

                # Проверяем прогноз на следующий час (hour[1])
                next_hour_forecast = forecast_hours[1]
                precip_mm_next_hour = next_hour_forecast.get('precip_mm', 0)
                condition_text_next_hour = next_hour_forecast['condition']['text']

                # Только если ожидается дождь
                if precip_mm_next_hour > 0 or 'rain' in condition_text_next_hour.lower():
                    WeatherAlert.objects.create(
                        city=city,
                        alert_type="Rain expected",
                        description="Forecast for next hour: rain",
                    )
                    alert_count += 1

                self.stdout.write(self.style.SUCCESS(
                    f"Updated weather for {city.name}: {current['temp_c']}°C, {current['humidity']}%, next hour: {condition_text_next_hour}"
                ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching weather for {city.name}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Weather updated for {weather_count} cities, rain alerts created: {alert_count}."
        ))

