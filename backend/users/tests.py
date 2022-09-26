from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class UserBaseTestCase(APITestCase):
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
        cls.auth_data = {
            key: cls.user_data[key] for key in ('email', 'password')
        }

    def _authorize(self):
        response = self.client.post(reverse('users:login'), self.auth_data)
        token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def _unauthorize(self):
        self.client.credentials()


class UserRegistrationTestCase(UserBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESPONSE_DATA_LENGTH = 5

    def test_valid_user_registration(self):
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), self.RESPONSE_DATA_LENGTH)
        for key in self.data:
            self.assertIn(key, response.data)
            self.assertEqual(response.data[key], self.user_data[key])
        self.assertIn('id', response.data)

    def test_invalid_user_registration(self):
        for key in self.user_data:
            data = self.user_data.copy()
            data.pop(key)
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_re_registration(self):
        response = self.client.post(self.url, self.user_data)
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthTestCase(UserBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESPONSE_DATA_LENGTH = 1
        cls.password_data = {
            'new_password': 'Asdfgh34',
            'current_password': cls.user_data['password'],
        }
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_set_password = cls.url + 'set_password/'

    def setUp(self):
        self.client.post(self.url, self.user_data)

    def test_get_authorization_token(self):
        response = self.client.post(self.url_login, self.auth_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('auth_token', response.data)
        self.assertEqual(len(response.data), self.RESPONSE_DATA_LENGTH)

    def test_authorized_destroy_authorization_token(self):
        self._authorize()
        response = self.client.post(self.url_logout)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_destroy_authorization_token(self):
        self._unauthorize()
        response = self.client.post(self.url_logout)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_set_password(self):
        self._authorize()
        response = self.client.post(self.url_set_password, self.password_data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_set_password(self):
        self._unauthorize()
        response = self.client.post(self.url_set_password, self.password_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailTestCase(UserBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESPONSE_DATA_LENGTH = 6
        cls.IS_SUBSCRIBED_DEFAULT = False
        cls.url_current_user = cls.url + 'me/'

    def setUp(self):
        response = self.client.post(self.url, self.user_data)
        self.url_detail = reverse(
            'users:user-detail', kwargs={'id': response.data['id']}
        )
        self.url_detail_non_exist = reverse(
            'users:user-detail', kwargs={'id': response.data['id'] + 1}
        )
        self.user_id = response.data['id']
        self._authorize()

    def test_authorized_user_profile(self):
        for value in (self.url_detail, self.url_current_user):
            with self.subTest(value=value):
                response = self.client.get(value)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), self.RESPONSE_DATA_LENGTH)
                for key in self.data:
                    self.assertIn(key, response.data)
                    self.assertEqual(response.data[key], self.user_data[key])
                self.assertIn('id', response.data)
                self.assertEqual(response.data['id'], self.user_id)
                self.assertIn('is_subscribed', response.data)
                self.assertEqual(
                    response.data['is_subscribed'], self.IS_SUBSCRIBED_DEFAULT
                )

    def test_unauthorized_user_profile(self):
        self._unauthorize()
        for value in (self.url_detail, self.url_current_user):
            with self.subTest(value=value):
                response = self.client.get(value)
                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED
                )

    def test_invalid_user_profile(self):
        response = self.client.get(self.url_detail_non_exist)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ManyUserTestCase(UserBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESPONSE_DATA_LENGTH = 4
        cls.RESULT_DETAIL_LENGTH = 6
        cls.IS_SUBSCRIBED_DEFAULT = False
        cls.PAGE_SIZE = 6
        cls.USERS_COUNT = 7
        cls.data_keys = ('count', 'next', 'previous', 'results')

    def setUp(self):
        response = self.client.post(self.url, self.user_data)
        self.user_id = response.data['id']
        self._authorize()

    def _create_users(self, count):
        for i in range(count):
            data = {
                **self.user_data,
                'username': f'user{i}',
                'email': f'user{i}@ya.ru',
            }
            self.client.post(self.url, data)

    def test_few_users_list(self):
        few_count = 2
        self._create_users(few_count)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data_keys))
        for key in self.data_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['results']), few_count + 1)

    def test_users_list(self):
        self._create_users(self.USERS_COUNT)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data_keys))
        for key in self.data_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['results']), self.PAGE_SIZE)

    def test_users_list_limit(self):
        limit_size = 5
        self._create_users(self.USERS_COUNT)
        response = self.client.get(f'{self.url}?limit={limit_size}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data_keys))
        for key in self.data_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['results']), limit_size)

    def test_users_list_result_detail(self):
        response = self.client.get(self.url)
        result = response.data['results'][0]
        self.assertEqual(len(result), self.RESULT_DETAIL_LENGTH)
        for key in self.data:
            self.assertIn(key, result)
            self.assertEqual(result[key], self.data[key])
        self.assertIn('id', result)
        self.assertEqual(result['id'], self.user_id)
        self.assertIn('is_subscribed', result)
        self.assertEqual(result['is_subscribed'], self.IS_SUBSCRIBED_DEFAULT)


class SubscriptionTestCase(UserBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.second_user_data = {
            'email': 'second@yandex.ru',
            'username': 'second',
            'first_name': 'Вася',
            'last_name': 'Пупкин',
            'password': 'Qwerty!2',
        }
        cls.third_user_data = {
            'email': 'third@yandex.ru',
            'username': 'third',
            'first_name': 'Вася',
            'last_name': 'Пупкин',
            'password': 'Qwerty!2',
        }

    def setUp(self):
        response = self.client.post(self.url, self.user_data)
        self.user_id = response.data['id']
        response = self.client.post(self.url, self.second_user_data)
        self.second_user_id = response.data['id']
        response = self.client.post(self.url, self.third_user_data)
        self.third_user_id = response.data['id']
        self.non_exist_user_id = self.third_user_id + 1
        self._authorize()

    def test_authorized_subscribe(self):
        url = (
            reverse('users:user-detail', kwargs={'id': self.second_user_id})
            + 'subscribe/'
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(
            reverse('users:user-detail', kwargs={'id': self.user_id})
            + 'subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(
            reverse('users:user-detail', kwargs={'id': self.non_exist_user_id})
            + 'subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_subscribe(self):
        url = (
            reverse('users:user-detail', kwargs={'id': self.second_user_id})
            + 'subscribe/'
        )
        self.client.credentials()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
