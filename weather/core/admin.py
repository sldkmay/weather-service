from django.contrib import admin
from django.contrib.auth.models import User
from .models import City, WeatherData, Forecast, WeatherCondition, UserFavoriteCity, WeatherAlert, UserProfile
from django.utils import timezone
from django.utils.html import format_html

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country', 'lat', 'lon', 'tz_id')

@admin.register(WeatherCondition)
class WeatherConditionAdmin(admin.ModelAdmin):
    list_display = ('text', 'code')

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('city', 'last_updated', 'localtime', 'temp_c', 'humidity', 'condition', 'is_day')

    def city_localtime(self, obj):
        tz_id = obj.city.tz_id or 'Europe/Moscow'
        local_tz = pytz.timezone(tz_id)
        local_dt = timezone.localtime(obj.last_updated, local_tz)
        return local_dt.strftime('%d.%m.%Y %H:%M')
    city_localtime.short_description = 'Local time'

@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ('city', 'forecast_date', 'max_temp_c', 'min_temp_c', 'condition')

@admin.register(UserFavoriteCity)
class UserFavoriteCityAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'added_at')
    readonly_fields = ('added_at',)

@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ('city', 'formatted_alert_time', 'alert_type')
    list_filter = ('alert_type', 'alert_time')
    search_fields = ('city__name', 'alert_type')
    readonly_fields = ('alert_time',)

    def formatted_alert_time(self, obj):
        return timezone.localtime(obj.alert_time).strftime('%d.%m.%Y %H:%M')
    formatted_alert_time.short_description = 'Alert time'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_favorite_cities')
    
    def get_favorite_cities(self, obj):
        return ", ".join([city.name for city in obj.favorite_cities.all()])
    get_favorite_cities.short_description = 'Favorite Cities'

admin.site.site_header = 'Weather Admin'
admin.site.site_title = 'Weather Admin Portal'
admin.site.index_title = 'Добро пожаловать в админку погодного сервиса'