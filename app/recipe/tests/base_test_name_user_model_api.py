from abc import ABC

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


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
        tag = self.model.objects.create(user=self.user, name="Fruity")

        res = self.client.get(self.list_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

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
