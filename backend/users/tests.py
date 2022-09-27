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

    def _create_users(self, count):
        ids = []
        for i in range(count):
            data = {
                **self.user_data,
                'username': f'user{i}',
                'email': f'user{i}@ya.ru',
            }
            response = self.client.post(self.url, data)
            ids.append(response.data['id'])
        return ids


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


class SeveralUsersTestCase(UserBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESULT_DETAIL_LENGTH = 6
        cls.IS_SUBSCRIBED_DEFAULT = False
        cls.PAGE_SIZE = 6
        cls.USERS_COUNT = 7
        cls.FEW_USERS_COUNT = 2
        cls.LIMIT_SIZE = 3
        cls.data_keys = ('count', 'next', 'previous', 'results')
        cls.pages = {1: 3, 2: 3, 3: 2}

    def setUp(self):
        response = self.client.post(self.url, self.user_data)
        self.user_id = response.data['id']
        self._authorize()

    def test_few_users_list(self):
        self._create_users(self.FEW_USERS_COUNT)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data_keys))
        for key in self.data_keys:
            self.assertIn(key, response.data)
        self.assertEqual(
            len(response.data['results']), self.FEW_USERS_COUNT + 1
        )

    def test_users_list(self):
        self._create_users(self.USERS_COUNT)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data_keys))
        for key in self.data_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['results']), self.PAGE_SIZE)

    def test_users_list_limit(self):
        self._create_users(self.USERS_COUNT)
        response = self.client.get(f'{self.url}?limit={self.LIMIT_SIZE}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data_keys))
        for key in self.data_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['results']), self.LIMIT_SIZE)
        for page, size in self.pages.items():
            response = self.client.get(f'{self.url}?page={page}&limit={size}')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), len(self.data_keys))
            for key in self.data_keys:
                self.assertIn(key, response.data)
            self.assertEqual(len(response.data['results']), size)

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
        cls.RESULT_DETAIL_LENGTH = 8
        cls.IS_SUBSCRIBED_DEFAULT = False
        cls.PAGE_SIZE = 6
        cls.USERS_COUNT = 7
        cls.FEW_USERS_COUNT = 2
        cls.LIMIT_SIZE = 3
        cls.NON_EXIST_USER_ID = 999
        cls.url_subscriptons = cls.url + 'subscriptions/'
        cls.data_keys = ('count', 'next', 'previous', 'results')
        cls.pages = {1: 3, 2: 3, 3: 2}
        cls.second_user_data = {
            'email': 'second@yandex.ru',
            'username': 'second',
            'first_name': 'Вася',
            'last_name': 'Пупкин',
            'password': 'Qwerty!2',
        }

    def _subscribe(self, ids):
        self._authorize()
        for id in ids:
            self.client.post(
                reverse('users:user-detail', kwargs={'id': id}) + 'subscribe/'
            )

    def setUp(self):
        response = self.client.post(self.url, self.user_data)
        self.user_id = response.data['id']
        response = self.client.post(self.url, self.second_user_data)
        self.second_user_id = response.data['id']

    def test_authorized_subscribe(self):
        self._authorize()
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
            reverse('users:user-detail', kwargs={'id': self.NON_EXIST_USER_ID})
            + 'subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_subscribe(self):
        self._unauthorize()
        url = (
            reverse('users:user-detail', kwargs={'id': self.second_user_id})
            + 'subscribe/'
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_subscriptions(self):
        self._authorize()
        response = self.client.get(self.url_subscriptons)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data_keys))
        for key in self.data_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['results']), 0)
        ids = self._create_users(self.USERS_COUNT)
        self._subscribe(ids)
        response = self.client.get(self.url_subscriptons)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.PAGE_SIZE)

    def test_unauthorized_subscriptions(self):
        self._unauthorize()
        response = self.client.get(self.url_subscriptons)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscriptions_limit(self):
        ids = self._create_users(self.USERS_COUNT)
        self._subscribe(ids)
        response = self.client.get(
            f'{self.url_subscriptons}?limit={self.LIMIT_SIZE}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data_keys))
        for key in self.data_keys:
            self.assertIn(key, response.data)
        self.assertEqual(len(response.data['results']), self.LIMIT_SIZE)
        for page, size in self.pages.items():
            response = self.client.get(
                f'{self.url_subscriptons}?page={page}&limit={size}'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), len(self.data_keys))
            for key in self.data_keys:
                self.assertIn(key, response.data)
            self.assertEqual(len(response.data['results']), size)

    def test_subscriptions_detail(self):
        self._subscribe([self.second_user_id])
        response = self.client.get(self.url_subscriptons)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data['results'][0]
        self.assertEqual(len(result), self.RESULT_DETAIL_LENGTH)
        for key in self.data:
            self.assertIn(key, result)
            self.assertEqual(result[key], self.second_user_data[key])
        self.assertIn('id', result)
        self.assertEqual(result['id'], self.second_user_id)
        self.assertIn('is_subscribed', result)
        self.assertEqual(result['is_subscribed'], True)
        self.assertIn('recipes', result)
        self.assertEqual(len(result['recipes']), 0)
        self.assertIn('recipes_count', result)
        self.assertEqual(len(result['recipes']), result['recipes_count'])

    def test_subscriptions_detail_resipes(self):
        self._subscribe([self.second_user_id])
        response = self.client.get(self.url_subscriptons)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data['results'][0]
        recipes = result['recipes']
        self.assertEqual(len(recipes), result['recipes_count'])
