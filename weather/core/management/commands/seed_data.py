import requests
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import City, WeatherCondition, WeatherData, Forecast, UserFavoriteCity, WeatherAlert, UserProfile
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime
import random

class Command(BaseCommand):
    help = "Fill DB with real API weather data (min 10 records per table where possible)"

    def handle(self, *args, **options):
        # Очистка
        City.objects.all().delete()
        WeatherCondition.objects.all().delete()
        WeatherData.objects.all().delete()
        Forecast.objects.all().delete()
        UserFavoriteCity.objects.all().delete()
        WeatherAlert.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # Города
        city_names = [
            'Moscow', 'Saint Petersburg', 'Volgograd', 'Yekaterinburg', 'Volzhskiy',
            'Nizhny Novgorod', 'Chelyabinsk', 'Samara', 'Omsk', 'Rostov-on-Don'
        ]
        cities = []
        for name in city_names:
            city = City.objects.create(
                name=name,
                region=f'Region {name}',
                country='Russia',
                lat=0, lon=0, tz_id='Europe/Moscow'
            )
            cities.append(city)

        # Пользователи
        users = []
        for i in range(10):
            user = User.objects.create_user(username=f'user{i+1}', password='password')
            users.append(user)

        api_key = getattr(settings, 'WEATHER_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR("WEATHER_API_KEY not set in settings.py"))
            return

        base_url = 'http://api.weatherapi.com/v1/forecast.json'

        # Для каждого города — запрос к API и заполнение WeatherData, Forecast, WeatherAlert
        for city in cities:
            params = {
                'key': api_key,
                'q': city.name,
                'days': 1,
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

                # --- WeatherCondition ---
                cond_data = data['current']['condition']
                condition, _ = WeatherCondition.objects.get_or_create(
                    code=cond_data.get('code', 0),
                    defaults={'text': cond_data.get('text', ''), 'icon_url': cond_data.get('icon', '')}
                )

                # --- WeatherData ---
                current = data['current']
                localtime_str = data['location']['localtime']  # строка вида '2023-07-03 19:00'
                localtime_dt = datetime.strptime(localtime_str, '%Y-%m-%d %H:%M')
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
                    localtime=localtime_dt,
                )

                # --- Forecast ---
                forecast_day = data['forecast']['forecastday'][0]
                Forecast.objects.create(
                    city=city,
                    forecast_date=forecast_day['date'],
                    max_temp_c=forecast_day['day']['maxtemp_c'],
                    min_temp_c=forecast_day['day']['mintemp_c'],
                    condition=condition,
                    chance_of_rain=forecast_day['day'].get('daily_chance_of_rain', 0),
                    chance_of_snow=forecast_day['day'].get('daily_chance_of_snow', 0),
                    uv=forecast_day['day']['uv'],
                )

                # --- WeatherAlert ---
                forecast_hours = forecast_day['hour']
                now = timezone.now()
                now_hour = now.hour
                next_hour_dt = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                next_hour = forecast_hours[now_hour + 1 if now_hour < 23 else 0]
                precip_mm_next_hour = next_hour.get('precip_mm', 0)
                condition_text_next_hour = next_hour['condition']['text']
                if precip_mm_next_hour > 0 or 'rain' in condition_text_next_hour.lower():
                    WeatherAlert.objects.create(
                        city=city,
                        alert_time=next_hour_dt,
                        alert_type="Rain expected",
                        description="Forecast for next hour: rain",
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching weather for {city.name}: {e}"))

        # UserProfile и favorite_cities (M2M)
        for user in users:
            profile = UserProfile.objects.create(user=user)
            fav_cities = random.sample(cities, k=random.randint(2, 4))
            profile.favorite_cities.set(fav_cities)

        self.stdout.write(self.style.SUCCESS("Test data from API created!"))

