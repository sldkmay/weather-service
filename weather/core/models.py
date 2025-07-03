from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    tz_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.region or ''}, {self.country or ''}"

class WeatherCondition(models.Model):
    text = models.CharField(max_length=100, unique=True)
    icon_url = models.URLField(blank=True, null=True)
    code = models.IntegerField(unique=True)

    def __str__(self):
        return self.text

class WeatherData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="weather")
    last_updated = models.DateTimeField()
    temp_c = models.DecimalField(max_digits=5, decimal_places=2)
    temp_f = models.DecimalField(max_digits=5, decimal_places=2)
    is_day = models.BooleanField()
    condition = models.ForeignKey(WeatherCondition, on_delete=models.SET_NULL, null=True, related_name='weather_data')
    wind_mph = models.DecimalField(max_digits=5, decimal_places=2)
    wind_kph = models.DecimalField(max_digits=5, decimal_places=2)
    wind_degree = models.IntegerField()
    wind_dir = models.CharField(max_length=10)
    pressure_mb = models.DecimalField(max_digits=6, decimal_places=2)
    pressure_in = models.DecimalField(max_digits=6, decimal_places=2)
    precip_mm = models.DecimalField(max_digits=6, decimal_places=2)
    precip_in = models.DecimalField(max_digits=6, decimal_places=2)
    humidity = models.IntegerField()
    cloud = models.IntegerField()
    feelslike_c = models.DecimalField(max_digits=5, decimal_places=2)
    feelslike_f = models.DecimalField(max_digits=5, decimal_places=2)
    windchill_c = models.DecimalField(max_digits=5, decimal_places=2)
    windchill_f = models.DecimalField(max_digits=5, decimal_places=2)
    heatindex_c = models.DecimalField(max_digits=5, decimal_places=2)
    heatindex_f = models.DecimalField(max_digits=5, decimal_places=2)
    dewpoint_c = models.DecimalField(max_digits=5, decimal_places=2)
    dewpoint_f = models.DecimalField(max_digits=5, decimal_places=2)
    vis_km = models.DecimalField(max_digits=5, decimal_places=2)
    vis_miles = models.DecimalField(max_digits=5, decimal_places=2)
    uv = models.DecimalField(max_digits=3, decimal_places=1)
    gust_mph = models.DecimalField(max_digits=5, decimal_places=2)
    gust_kph = models.DecimalField(max_digits=5, decimal_places=2)
    localtime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Weather for {self.city.name} at {self.last_updated}"

class Forecast(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="forecasts")
    forecast_date = models.DateField()
    max_temp_c = models.DecimalField(max_digits=5, decimal_places=2)
    min_temp_c = models.DecimalField(max_digits=5, decimal_places=2)
    condition = models.ForeignKey(WeatherCondition, on_delete=models.SET_NULL, null=True, related_name='forecasts')
    chance_of_rain = models.IntegerField(blank=True, null=True)
    chance_of_snow = models.IntegerField(blank=True, null=True)
    uv = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return f"Forecast for {self.city.name} on {self.forecast_date}"

class UserFavoriteCity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_cities')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='fans')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'city')

    def __str__(self):
        return f"{self.user.username} likes {self.city.name}"

class WeatherAlert(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='alerts')
    alert_time = models.DateTimeField()
    alert_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Alert for {self.city.name} at {self.alert_time}: {self.alert_type}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_cities = models.ManyToManyField(City, related_name='profile_fans')

    def __str__(self):
        return self.user.username
