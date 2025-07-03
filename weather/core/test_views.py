from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import City, UserFavoriteCity

class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.city = City.objects.create(name='Москва', country='Россия')

    def test_index_page_accessible(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_add_favorite_requires_login(self):
        response = self.client.get(reverse('add_favorite_city'))
        self.assertNotEqual(response.status_code, 200)
        self.assertIn('/accounts/login/', response.url)

    def test_add_favorite_success(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('add_favorite_city'), {'city': self.city.id}, follow=True)
        self.assertRedirects(response, reverse('favorite_city_added'))
        self.assertTrue(UserFavoriteCity.objects.filter(user=self.user, city=self.city).exists())

    def test_add_favorite_duplicate(self):
        self.client.login(username='testuser', password='12345')
        UserFavoriteCity.objects.create(user=self.user, city=self.city)
        response = self.client.post(reverse('add_favorite_city'), {'city': self.city.id}, follow=True)
        # Должна быть ошибка уникальности или другая реакция
        self.assertContains(response, 'уже есть', status_code=200)

    def test_favorite_added_page(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('favorite_city_added'))
        self.assertEqual(response.status_code, 200) 