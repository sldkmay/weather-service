import requests
from django.core.management.base import BaseCommand
from core.models import City, WeatherCondition, WeatherData
from django.utils import timezone
from django.conf import settings
from datetime import datetime

class Command(BaseCommand):
    help = 'Синхронизирует погоду для всех городов из базы с внешним API'

    def handle(self, *args, **options):
        api_key = getattr(settings, 'WEATHER_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR('API ключ не найден в настройках!'))
            return

        for city in City.objects.all():
            self.stdout.write(f'Обновление погоды для: {city.name}')
            url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city.name}&lang=ru'
            response = requests.get(url)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Ошибка API для {city.name}: {response.text}'))
                continue

            data = response.json()
            condition_data = data['current']['condition']
            condition, _ = WeatherCondition.objects.get_or_create(
                code=condition_data['code'],
                defaults={'text': condition_data['text'], 'icon_url': condition_data['icon']}
            )
            # Обновить текст и иконку, если изменились
            condition.text = condition_data['text']
            condition.icon_url = condition_data['icon']
            condition.save()

            # Преобразуем localtime в datetime
            localtime_str = data['location']['localtime']
            try:
                localtime = datetime.strptime(localtime_str, '%Y-%m-%d %H:%M')
            except Exception:
                localtime = timezone.now()

            WeatherData.objects.update_or_create(
                city=city,
                defaults={
                    'last_updated': timezone.now(),
                    'temp_c': data['current']['temp_c'],
                    'temp_f': data['current']['temp_f'],
                    'is_day': data['current']['is_day'],
                    'condition': condition,
                    'wind_mph': data['current']['wind_mph'],
                    'wind_kph': data['current']['wind_kph'],
                    'wind_degree': data['current']['wind_degree'],
                    'wind_dir': data['current']['wind_dir'],
                    'pressure_mb': data['current']['pressure_mb'],
                    'pressure_in': data['current']['pressure_in'],
                    'precip_mm': data['current']['precip_mm'],
                    'precip_in': data['current']['precip_in'],
                    'humidity': data['current']['humidity'],
                    'cloud': data['current']['cloud'],
                    'feelslike_c': data['current']['feelslike_c'],
                    'feelslike_f': data['current']['feelslike_f'],
                    'windchill_c': data['current'].get('windchill_c', data['current']['feelslike_c']),
                    'windchill_f': data['current'].get('windchill_f', data['current']['feelslike_f']),
                    'heatindex_c': data['current'].get('heatindex_c', data['current']['feelslike_c']),
                    'heatindex_f': data['current'].get('heatindex_f', data['current']['feelslike_f']),
                    'dewpoint_c': data['current'].get('dewpoint_c', 0),
                    'dewpoint_f': data['current'].get('dewpoint_f', 0),
                    'vis_km': data['current']['vis_km'],
                    'vis_miles': data['current']['vis_miles'],
                    'uv': data['current']['uv'],
                    'gust_mph': data['current']['gust_mph'],
                    'gust_kph': data['current']['gust_kph'],
                    'localtime': localtime,
                }
            )

            # Обновление региона, если он отличается или отсутствует
            api_region = data['location'].get('region', '')
            if api_region and city.region != api_region:
                city.region = api_region
                city.save(update_fields=['region'])

            self.stdout.write(self.style.SUCCESS(f'Погода для {city.name} обновлена!')) 