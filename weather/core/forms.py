from django import forms
from .models import UserFavoriteCity, WeatherData
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserFavoriteCityForm(forms.ModelForm):
    class Meta:
        model = UserFavoriteCity
        fields = ['city']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        city = cleaned_data.get('city')
        if self.user and city:
            if UserFavoriteCity.objects.filter(user=self.user, city=city).exists():
                self.add_error('city', 'Этот город уже есть в ваших избранных.')
        return cleaned_data

class WeatherDataForm(forms.ModelForm):
    class Meta:
        model = WeatherData
        fields = ['city']

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Пароли не совпадают.')
        return cleaned_data 