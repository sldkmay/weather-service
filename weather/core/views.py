from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import City, WeatherData, UserFavoriteCity, WeatherCondition
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from .forms import UserFavoriteCityForm, WeatherDataForm, SignUpForm
from django_filters.views import FilterView
from .filters import CityFilter
from django.views import View
from django.contrib import messages
from django.conf import settings
import requests
from datetime import datetime
from django.utils import timezone
import django.db
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

def index(request):
    return render(request, 'core/index.html')

def city_weather_list(request):
    weather_data = WeatherData.objects.all().order_by('-last_updated')
    context = {
        'weather_data': weather_data,
    }
    return render(request, 'core/city_weather_list.html', context)

class UserFavoriteCityCreateView(LoginRequiredMixin, CreateView):
    model = UserFavoriteCity
    form_class = UserFavoriteCityForm
    template_name = 'core/add_favorite_city.html'
    success_url = reverse_lazy('favorite_city_added')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class UserFavoriteCityUpdateView(LoginRequiredMixin, UpdateView):
    model = UserFavoriteCity
    form_class = UserFavoriteCityForm
    template_name = 'core/add_favorite_city.html'
    success_url = reverse_lazy('my_weatherdata_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Ensure the user cannot change the owner
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_queryset(self):
        # Only allow users to edit their own favorite cities
        return UserFavoriteCity.objects.filter(user=self.request.user)

class CityListView(FilterView):
    model = City
    template_name = 'core/city_list.html'
    filterset_class = CityFilter
    context_object_name = 'cities'
    paginate_by = 10

class WeatherDataListView(ListView):
    model = WeatherData
    template_name = 'core/city_weather_list.html'
    context_object_name = 'weather_data'
    ordering = ['-last_updated']

class WeatherDataCreateView(CreateView):
    model = WeatherData
    form_class = WeatherDataForm
    template_name = 'core/weatherdata_form.html'
    success_url = reverse_lazy('my_weatherdata_list')

    def form_valid(self, form):
        city = form.cleaned_data['city']
        if WeatherData.objects.filter(city=city).exists():
            form.add_error('city', 'Погодные данные для этого города уже существуют.')
            return self.form_invalid(form)
        api_key = getattr(settings, 'WEATHER_API_KEY', None)
        url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city.name}&lang=ru'
        response = requests.get(url)
        if response.status_code != 200:
            form.add_error('city', f'Ошибка API: {response.text}')
            return self.form_invalid(form)
        data = response.json()
        condition_data = data['current']['condition']
        condition, _ = WeatherCondition.objects.get_or_create(
            code=condition_data['code'],
            defaults={'text': condition_data['text'], 'icon_url': condition_data['icon']}
        )
        condition.text = condition_data['text']
        condition.icon_url = condition_data['icon']
        condition.save()
        localtime_str = data['location']['localtime']
        try:
            naive_localtime = datetime.strptime(localtime_str, '%Y-%m-%d %H:%M')
            localtime = timezone.make_aware(naive_localtime, timezone.get_current_timezone())
        except Exception:
            localtime = timezone.now()
        try:
            WeatherData.objects.create(
                city=city,
                last_updated=timezone.now(),
                temp_c=data['current']['temp_c'],
                temp_f=data['current']['temp_f'],
                is_day=data['current']['is_day'],
                condition=condition,
                wind_mph=data['current']['wind_mph'],
                wind_kph=data['current']['wind_kph'],
                wind_degree=data['current']['wind_degree'],
                wind_dir=data['current']['wind_dir'],
                pressure_mb=data['current']['pressure_mb'],
                pressure_in=data['current']['pressure_in'],
                precip_mm=data['current']['precip_mm'],
                precip_in=data['current']['precip_in'],
                humidity=data['current']['humidity'],
                cloud=data['current']['cloud'],
                feelslike_c=data['current']['feelslike_c'],
                feelslike_f=data['current']['feelslike_f'],
                windchill_c=data['current'].get('windchill_c', data['current']['feelslike_c']),
                windchill_f=data['current'].get('windchill_f', data['current']['feelslike_f']),
                heatindex_c=data['current'].get('heatindex_c', data['current']['feelslike_c']),
                heatindex_f=data['current'].get('heatindex_f', data['current']['feelslike_f']),
                dewpoint_c=data['current'].get('dewpoint_c', 0),
                dewpoint_f=data['current'].get('dewpoint_f', 0),
                vis_km=data['current']['vis_km'],
                vis_miles=data['current']['vis_miles'],
                uv=data['current']['uv'],
                gust_mph=data['current']['gust_mph'],
                gust_kph=data['current']['gust_kph'],
                localtime=localtime,
            )
        except django.db.IntegrityError as e:
            form.add_error('city', f'Ошибка сохранения: {e}')
            return self.form_invalid(form)
        return redirect(self.success_url)


class WeatherDataDeleteView(DeleteView):
    model = WeatherData
    template_name = 'core/weatherdata_confirm_delete.html'
    success_url = reverse_lazy('my_weatherdata_list')

class WeatherDataDetailView(DetailView):
    model = WeatherData
    template_name = 'core/weatherdata_detail.html'
    context_object_name = 'weatherdata'

class WeatherDataSyncAllView(View):
    def post(self, request, *args, **kwargs):
        api_key = getattr(settings, 'WEATHER_API_KEY', None)
        if not api_key:
            messages.error(request, 'API ключ не найден в настройках!')
            return redirect('my_weatherdata_list')
        for city in City.objects.all():
            url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city.name}&lang=ru'
            response = requests.get(url)
            if response.status_code != 200:
                continue
            data = response.json()
            condition_data = data['current']['condition']
            condition, _ = WeatherCondition.objects.get_or_create(
                code=condition_data['code'],
                defaults={'text': condition_data['text'], 'icon_url': condition_data['icon']}
            )
            condition.text = condition_data['text']
            condition.icon_url = condition_data['icon']
            condition.save()
            localtime_str = data['location']['localtime']
            try:
                naive_localtime = datetime.strptime(localtime_str, '%Y-%m-%d %H:%M')
                localtime = timezone.make_aware(naive_localtime, timezone.get_current_timezone())
            except Exception:
                localtime = timezone.now()
            # Deduplicate existing WeatherData for the city before upserting
            existing_qs = WeatherData.objects.filter(city=city).order_by('-last_updated')
            if existing_qs.count() > 1:
                # Keep the most recent; delete older duplicates
                for duplicate in existing_qs[1:]:
                    duplicate.delete()
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
        messages.success(request, 'Синхронизация завершена!')
        return redirect('my_weatherdata_list')

class AllWeatherDataListView(ListView):
    model = WeatherData
    template_name = 'core/all_weather_list.html'
    context_object_name = 'weather_data'
    ordering = ['-last_updated']

class MyWeatherDataListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    redirect_field_name = 'next'
    model = WeatherData
    template_name = 'core/my_weather_list.html'
    context_object_name = 'weather_data'
    ordering = ['-last_updated']

    def get_queryset(self):
        return WeatherData.objects.filter(city__fans__user=self.request.user).distinct()

@login_required
@require_POST
def unfavorite_city(request, pk):
    # pk is City id; remove favorite relation for current user
    UserFavoriteCity.objects.filter(user=request.user, city_id=pk).delete()
    messages.success(request, 'Город удалён из избранного.')
    return redirect('my_weatherdata_list')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})