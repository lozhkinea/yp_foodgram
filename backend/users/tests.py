from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class UserRegTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESPONSE_DATA_LENGTH = 5
        cls.url = reverse('users:user-list')
        cls.user_data = {
            'email': 'vpupkin@yandex.ru',
            'username': 'vasya.pupkin',
            'first_name': 'Вася',
            'last_name': 'Пупкин',
            'password': 'Qwerty!2',
        }

    def test_valid_user_registration(self):
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), self.RESPONSE_DATA_LENGTH)
        data = self.user_data.copy()
        data.pop('password')
        for key in data:
            self.assertIn(key, response.data)
            self.assertEqual(response.data[key], self.user_data[key])
        self.assertIn('id', response.data)

    def test_valid_user_re_registration(self):
        response = self.client.post(self.url, self.user_data)
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_user_registration(self):
        for key in self.user_data:
            wrong_data = self.user_data.copy()
            wrong_data.pop(key)
            response = self.client.post(self.url, wrong_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESPONSE_DATA_LENGTH = 1
        cls.url = reverse('users:user-list')
        cls.user_data = {
            'email': 'vpupkin@yandex.ru',
            'username': 'vasya.pupkin',
            'first_name': 'Вася',
            'last_name': 'Пупкин',
            'password': 'Qwerty!2',
        }
        cls.auth_data = {
            key: cls.user_data[key] for key in ('email', 'password')
        }
        cls.password_data = {
            'new_password': 'Asdfgh34',
            'current_password': cls.user_data['password'],
        }

    def setUp(self):
        self.client.post(self.url, self.user_data)

    def _authorize(self):
        response = self.client.post(reverse('users:login'), self.auth_data)
        token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_get_authorization_token(self):
        response = self.client.post(reverse('users:login'), self.auth_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('auth_token', response.data)
        self.assertEqual(len(response.data), self.RESPONSE_DATA_LENGTH)

    def test_valid_destroy_authorization_token(self):
        self._authorize()
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_destroy_authorization_token(self):
        self.client.credentials()
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_change_password(self):
        self._authorize()
        url = self.url + 'set_password/'
        response = self.client.post(url, self.password_data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_change_password(self):
        self.client.credentials()
        url = self.url + 'set_password/'
        response = self.client.post(url, self.password_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('users:user-list')
        cls.data = {
            'email': 'vpupkin@yandex.ru',
            'username': 'vasya.pupkin',
            'first_name': 'Вася',
            'last_name': 'Пупкин',
        }
        cls.user_data = {**cls.data, 'password': 'Qwerty!2'}
        cls.response_data = {**cls.data, 'id': 1, 'is_subscribed': False}
        cls.url_detail = reverse('users:user-detail', kwargs={'id': 1})
        cls.url_non_exist = reverse('users:user-detail', kwargs={'id': 2})
        cls.url_current_user = cls.url + 'me/'

    def setUp(self):
        self.client.post(self.url, self.user_data)
        auth_data = {key: self.user_data[key] for key in ('email', 'password')}
        response = self.client.post(reverse('users:login'), auth_data)
        token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_authorized_user_profile(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.response_data))
        for key in self.response_data:
            self.assertIn(key, response.data)
            self.assertEqual(response.data[key], self.response_data[key])

    def test_unauthorized_user_profile(self):
        self.client.credentials()
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_user_profile(self):
        response = self.client.get(self.url_non_exist)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authorized_current_user(self):
        response = self.client.get(self.url_current_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.response_data))
        for key in self.response_data:
            self.assertIn(key, response.data)
            self.assertEqual(response.data[key], self.response_data[key])

    def test_unauthorized_current_user(self):
        self.client.credentials()
        response = self.client.get(self.url_current_user)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_list(self):
        response_keys = ('count', 'next', 'previous', 'results')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(response_keys))
        for key in response_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['results']), 1)
        for key in self.response_data:
            item = response.data['results'][0]
            self.assertEqual(len(item), len(self.response_data))
            self.assertIn(key, item)
            self.assertEqual(item[key], self.response_data[key])
