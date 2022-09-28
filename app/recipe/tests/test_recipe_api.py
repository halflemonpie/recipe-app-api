"""
Test for recipe API
"""

from decimal import Decimal
from email.policy import default

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params):
    # create and return a sample recipe
    default = {
        'title': 'This is a Sample Title',
        'time_minutes': 24,
        'price': Decimal('7.88'),
        'description': 'The sample description is here!!',
        'link': 'HTTP://example.com/recipe.pdf',
    }
    default.update(params)

    recipe = Recipe.objects.create(user=user, **default)
    return recipe


class PublicRecipeAPITests(TestCase):
    # test for unauthorized API request
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # test if auth is required
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    # test for authorized API request
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpassword123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        # test for retrieving a list of recipes
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        # test if the recipe is limited to authenticated user
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'otheruserpassword',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
