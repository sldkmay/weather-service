from django.urls import path
from . import views
from .views import UserFavoriteCityCreateView, CityListView, WeatherDataListView, WeatherDataCreateView, WeatherDataUpdateView, WeatherDataDeleteView, WeatherDataDetailView, WeatherDataSyncAllView, AllWeatherDataListView, MyWeatherDataListView, signup
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="index"), name="logout"),
    path("cities/", AllWeatherDataListView.as_view(), name="all_weatherdata_list"),
    path("my-cities/", MyWeatherDataListView.as_view(), name="my_weatherdata_list"),
    path("my-cities/add/", WeatherDataCreateView.as_view(), name="weatherdata_add"),
    path("my-cities/<int:pk>/", WeatherDataDetailView.as_view(), name="weatherdata_detail"),
    path("my-cities/<int:pk>/edit/", WeatherDataUpdateView.as_view(), name="weatherdata_edit"),
    path("my-cities/<int:pk>/delete/", WeatherDataDeleteView.as_view(), name="weatherdata_delete"),
    path("my-cities/sync-all/", WeatherDataSyncAllView.as_view(), name="weatherdata_sync_all"),
    path("add-favorite/", UserFavoriteCityCreateView.as_view(), name="add_favorite_city"),
    path("favorite-added/", TemplateView.as_view(template_name="core/favorite_city_added.html"), name="favorite_city_added"),
    path('city-filter/', CityListView.as_view(), name='city_filter'),
    path("signup/", signup, name="signup"),
]