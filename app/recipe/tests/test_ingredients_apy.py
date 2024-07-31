from django.urls import reverse
from django.test import TestCase

from core.models import Ingredient

from recipe.serializers import IngredientSerializer
from recipe.tests.base_test_name_user_model_api import BasePublicRecipeModelApiTests, BasePrivateNameUserModelApiTest

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(BasePublicRecipeModelApiTests, TestCase):
    model = Ingredient
    url = INGREDIENTS_URL


class PrivateTagsApiTests(BasePrivateNameUserModelApiTest, TestCase):
    model = Ingredient
    serializer = IngredientSerializer
    list_url = INGREDIENTS_URL
    detail_url_reversal = 'recipe:ingredient-detail'

