from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class UsersTests(APITestCase):
    def test_create_user(self):
        url = reverse('users:user-list')
        data = {
            "email": "vpupkin@yandex.ru",
            "username": "vasya.pupkin",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "password": "Qwerty!2",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertIn('id', response.data)
        data.pop("password")
        for key in data:
            self.assertEqual(response.data[key], data[key])

    def test_change_password(self):
        url = reverse('users:set_password')
        data = {"new_password": "Qwerty!2", "current_password": "Asdfg34"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
