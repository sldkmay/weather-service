from django.contrib import admin
from django.contrib.auth.models import User
from .models import City, WeatherData, Forecast, WeatherCondition, UserFavoriteCity, WeatherAlert, UserProfile
from django.utils import timezone
from django.utils.html import format_html
from zoneinfo import ZoneInfo


City._meta.verbose_name = "Город"
City._meta.verbose_name_plural = "Города"

WeatherCondition._meta.verbose_name = "Погодное состояние"
WeatherCondition._meta.verbose_name_plural = "Погодные состояния"

WeatherData._meta.verbose_name = "Погодные данные"
WeatherData._meta.verbose_name_plural = "Погодные данные"

Forecast._meta.verbose_name = "Прогноз"
Forecast._meta.verbose_name_plural = "Прогнозы"

UserFavoriteCity._meta.verbose_name = "Избранный город пользователя"
UserFavoriteCity._meta.verbose_name_plural = "Избранные города пользователей"

WeatherAlert._meta.verbose_name = "Погодное предупреждение"
WeatherAlert._meta.verbose_name_plural = "Погодные предупреждения"

UserProfile._meta.verbose_name = "Профиль пользователя"
UserProfile._meta.verbose_name_plural = "Профили пользователей"


class WeatherDataInline(admin.TabularInline):
    model = WeatherData
    extra = 0
    fields = ('last_updated', 'temp_c', 'humidity', 'is_day')
    readonly_fields = ('last_updated',)

class ForecastInline(admin.TabularInline):
    model = Forecast
    extra = 0
    fields = ('forecast_date', 'max_temp_c', 'min_temp_c', 'condition')

class WeatherAlertInline(admin.TabularInline):
    model = WeatherAlert
    extra = 0
    fields = ('alert_time', 'alert_type')

class UserFavoriteCityInline(admin.TabularInline):
    model = UserFavoriteCity
    extra = 0
    fields = ('user', 'added_at')
    raw_id_fields = ('user',)
    readonly_fields = ('added_at',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country', 'lat', 'lon', 'tz_id')
    list_display_links = ('name',)
    list_filter = ('country', 'region')
    search_fields = ('name', 'region', 'country')
    inlines = [WeatherDataInline, ForecastInline, WeatherAlertInline, UserFavoriteCityInline]

    def get_readonly_fields(self, request, obj=None):
        return ('id',)

@admin.register(WeatherCondition)
class WeatherConditionAdmin(admin.ModelAdmin):
    list_display = ('text', 'code')
    list_display_links = ('text',)
    search_fields = ('text', 'code')

    def get_readonly_fields(self, request, obj=None):
        return ('id',)

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('city', 'last_updated', 'city_localtime', 'temp_c', 'humidity', 'condition', 'is_day')
    list_display_links = ('city',)
    list_filter = ('is_day', 'condition', 'city')
    date_hierarchy = 'last_updated'
    search_fields = ('city__name',)
    raw_id_fields = ('city', 'condition')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('id', 'city')
        return ('id',)

    @admin.display(description='Local time')
    def city_localtime(self, obj):
        tz_id = obj.city.tz_id or 'Europe/Moscow'
        try:
            local_tz = ZoneInfo(tz_id)
            local_dt = obj.last_updated.astimezone(local_tz)
            return local_dt.strftime('%d.%m.%Y %H:%M')
        except Exception:
            return timezone.localtime(obj.last_updated).strftime('%d.%m.%Y %H:%M')

@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ('city', 'forecast_date', 'max_temp_c', 'min_temp_c', 'condition')
    list_display_links = ('city',)
    list_filter = ('forecast_date', 'condition')
    date_hierarchy = 'forecast_date'
    search_fields = ('city__name',)
    raw_id_fields = ('city', 'condition')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('id', 'city')
        return ('id',)

@admin.register(UserFavoriteCity)
class UserFavoriteCityAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'added_at')
    list_display_links = ('user', 'city')
    list_filter = ('added_at',)
    date_hierarchy = 'added_at'
    search_fields = ('user__username', 'city__name')
    raw_id_fields = ('user', 'city')
    readonly_fields = ('added_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('id', 'user', 'added_at')
        return ('id', 'added_at')

@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ('city', 'formatted_alert_time', 'alert_type')
    list_display_links = ('city', 'alert_type')
    list_filter = ('alert_type', 'alert_time')
    date_hierarchy = 'alert_time'
    search_fields = ('city__name', 'alert_type')
    raw_id_fields = ('city',)
    readonly_fields = ('alert_time',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('id', 'city', 'alert_time')
        return ('id', 'alert_time')

    @admin.display(description='Alert time')
    def formatted_alert_time(self, obj):
        return timezone.localtime(obj.alert_time).strftime('%d.%m.%Y %H:%M')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_favorite_cities')
    search_fields = ('user__username', 'favorite_cities__name')
    raw_id_fields = ('user',)
    filter_horizontal = ('favorite_cities',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('id', 'user')
        return ('id',)

    @admin.display(description='Favorite Cities')
    def get_favorite_cities(self, obj):
        return ", ".join([city.name for city in obj.favorite_cities.all()])

admin.site.site_header = 'Weather Admin'
admin.site.site_title = 'Weather Admin Portal'
admin.site.index_title = 'Добро пожаловать в админку погодного сервиса'