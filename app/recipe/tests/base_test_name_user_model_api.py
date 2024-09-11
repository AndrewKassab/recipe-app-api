from abc import ABC

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient, Tag


RELATED_FIELD_MAP = {
    Ingredient: 'ingredients',
    Tag: 'tags',
}


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create(email=email, password=password)


class BasePublicRecipeModelApiTests(object):
    model = None
    url = None

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class BasePrivateNameUserModelApiTest(object):
    model = None
    serializer = None
    list_url = None
    detail_url_reversal = None

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def detail_url(self, model_id):
        return reverse(self.detail_url_reversal, args=[model_id])

    def test_retrieve_model(self):
        self.model.objects.create(user=self.user, name='Vegan')
        self.model.objects.create(user=self.user, name='Dessert')

        res = self.client.get(self.list_url)

        tags = self.model.objects.all().order_by('-name')
        serializer = self.serializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_model_limited_to_user(self):
        user2 = create_user(email='user2@example.com')
        self.model.objects.create(user=user2, name="Meat")
        item = self.model.objects.create(user=self.user, name="Fruity")

        res = self.client.get(self.list_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], item.name)
        self.assertEqual(res.data[0]['id'], item.id)

    def test_update_model(self):
        model= self.model.objects.create(user=self.user, name="Name")

        payload = {'name': 'New Name'}
        url = self.detail_url(model.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        model.refresh_from_db()
        self.assertEqual(model.name, payload['name'])

    def test_delete_model(self):
        model = self.model.objects.create(user=self.user, name="Name")

        url = self.detail_url(model.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        models = self.model.objects.filter(user=self.user)
        self.assertFalse(models.exists())

    def test_filter_model_assigned_to_recipes(self):
        obj1 = self.model.objects.create(user=self.user, name="Object 1")
        obj2 = self.model.objects.create(user=self.user, name="Object 2")
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        getattr(recipe, RELATED_FIELD_MAP.get(self.model)).add(obj1)

        res = self.client.get(self.list_url, {'assigned_only': 1})

        s1 = self.serializer(obj1)
        s2 = self.serializer(obj2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_objects_unique(self):
        obj = self.model.objects.create(user=self.user, name="Object")
        self.model.objects.create(user=self.user, name="Different Object")
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user
        )

        getattr(recipe1, RELATED_FIELD_MAP.get(self.model)).add(obj)
        getattr(recipe2, RELATED_FIELD_MAP.get(self.model)).add(obj)

        res = self.client.get(self.list_url, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

