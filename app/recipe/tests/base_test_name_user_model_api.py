from abc import ABC

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create(email=email, password=password)


class BasePublicNameUserModelTests(TestCase):
    model = None
    url = None

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class BasePrivateNameUserModelTest(TestCase):
    model = None
    serializer = None
    url = None
    detail_url_reversal = None

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_model(self):
        self.model.objects.create(user=self.user, name='Vegan')
        self.model.objects.create(user=self.user, name='Dessert')

        res = self.client.get(self.url)

        tags = self.model.objects.all().order_by('-name')
        serializer = self.serializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
