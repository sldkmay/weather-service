from django.test import TestCase
from django.contrib.auth.models import User
from .models import City, WeatherCondition, WeatherData, UserFavoriteCity
from datetime import datetime

class ModelStrTest(TestCase):
    def setUp(self):
        self.city = City.objects.create(name='Москва', country='Россия')
        self.condition = WeatherCondition.objects.create(text='Солнечно', code=1000)
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.weather = WeatherData.objects.create(
            city=self.city,
            last_updated=datetime.now(),
            temp_c=20,
            temp_f=68,
            is_day=True,
            condition=self.condition,
            wind_mph=5,
            wind_kph=8,
            wind_degree=90,
            wind_dir='E',
            pressure_mb=1012,
            pressure_in=29.88,
            precip_mm=0,
            precip_in=0,
            humidity=50,
            cloud=0,
            feelslike_c=20,
            feelslike_f=68,
            windchill_c=20,
            windchill_f=68,
            heatindex_c=20,
            heatindex_f=68,
            dewpoint_c=10,
            dewpoint_f=50,
            vis_km=10,
            vis_miles=6,
            uv=5,
            gust_mph=7,
            gust_kph=11,
            localtime=datetime.now()
        )
        self.favorite = UserFavoriteCity.objects.create(user=self.user, city=self.city)

    def test_city_str(self):
        self.assertIn('Москва', str(self.city))

    def test_condition_str(self):
        self.assertEqual(str(self.condition), 'Солнечно')

    def test_weatherdata_str(self):
        self.assertIn('Москва', str(self.weather))

    def test_favorite_str(self):
        self.assertIn('testuser', str(self.favorite)) 