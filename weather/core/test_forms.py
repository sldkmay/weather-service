from django.test import TestCase
from django.contrib.auth.models import User
from .models import City, UserFavoriteCity
from .forms import UserFavoriteCityForm

class UserFavoriteCityFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.city = City.objects.create(name='Москва', country='Россия')

    def test_valid_form(self):
        form = UserFavoriteCityForm(data={'city': self.city.id}, user=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = UserFavoriteCityForm(data={'city': ''}, user=self.user)
        self.assertFalse(form.is_valid())

    def test_duplicate_favorite(self):
        UserFavoriteCity.objects.create(user=self.user, city=self.city)
        form = UserFavoriteCityForm(data={'city': self.city.id}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('Этот город уже есть в ваших избранных.', form.errors['city']) 