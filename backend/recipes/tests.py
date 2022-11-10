from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .models import Ingredient, Tag


class RecipeBaseTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tags = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#E26C2D', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#E26C2D', 'slug': 'dinner'},
        ]
        Tag.objects.bulk_create([Tag(**tag) for tag in cls.tags])
        cls.ingredients = [
            {'name': 'абрикосы', 'measurement_unit': 'г'},
            {'name': 'абрикосовый сок', 'measurement_unit': 'стакан'},
        ]
        Ingredient.objects.bulk_create(
            [Ingredient(**ingredient) for ingredient in cls.ingredients]
        )


class TagsTestCase(RecipeBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESPONSE_DATA_LENGTH = 4
        cls.url_list = reverse('recipes:tag-list')
        cls.url_detail = reverse('recipes:tag-detail', kwargs={'pk': 1})
        cls.url_detail_non_exist = reverse(
            'recipes:tag-detail', kwargs={'pk': 999}
        )
        cls.data_error = {'detail': 'Страница не найдена.'}

    def test_tag_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.tags))
        for key in self.tags[0]:
            self.assertIn(key, response.data[0])
        self.assertIn('id', response.data[0])

    def test_tag_detail(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.RESPONSE_DATA_LENGTH)
        for key in self.tags[0]:
            self.assertIn(key, response.data)
        self.assertIn('id', response.data)

    def test_tag_detail_invalid(self):
        response = self.client.get(self.url_detail_non_exist)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(response.data), len(self.data_error))
        for key in self.data_error:
            self.assertIn(key, response.data)
            self.assertEqual(self.data_error[key], response.data[key])


class IngredientsTestCase(RecipeBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RESPONSE_DATA_LENGTH = 3
        cls.url_list = reverse('recipes:ingredient-list')
        cls.url_detail = reverse('recipes:ingredient-detail', kwargs={'pk': 1})
        cls.url_search = cls.url_list + '?name=абрикос'
        cls.url_search_ = {
            cls.url_list + '?name=неабрикос': 0,
            cls.url_list + '?name=неабрикос': 1,
            cls.url_list + '?name=абрикос': 2,
        }

    def test_ingredient_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.ingredients))
        for key in self.ingredients[0]:
            self.assertIn(key, response.data[0])
        self.assertIn('id', response.data[0])

    def test_ingredient_detail(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.RESPONSE_DATA_LENGTH)
        for key in self.ingredients[0]:
            self.assertIn(key, response.data)
        self.assertIn('id', response.data)

    def test_ingredient_seacrh(self):
        response = self.client.get(self.url_search)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.ingredients))
        for key in self.ingredients[0]:
            self.assertIn(key, response.data[0])
        self.assertIn('id', response.data[0])
