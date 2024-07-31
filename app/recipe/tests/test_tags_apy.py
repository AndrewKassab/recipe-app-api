from django.urls import reverse
from django.test import TestCase

from core.models import Tag

from recipe.serializers import TagSerializer
from recipe.tests.base_test_name_user_model_api import BasePrivateNameUserModelApiTest, BasePublicRecipeModelApiTests

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(BasePublicRecipeModelApiTests, TestCase):
    model = Tag
    url = TAGS_URL


class PrivateTagsApiTests(BasePrivateNameUserModelApiTest, TestCase):
    model = Tag
    serializer = TagSerializer
    list_url = TAGS_URL
    detail_url_reversal = 'recipe:tag-detail'


