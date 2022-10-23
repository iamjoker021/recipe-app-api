"""
Test Recipe API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    """Create and return recipe"""
    defaults = {
        "title": "Sample Recipe title",
        "time_minutes": 7,
        "price": Decimal("5.99"),
        "description": "Sample description",
        "link": "http://example.com/recipe.png",
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test Unauth API req"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test Auth recipe API req"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@mail.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrive a list of recipe"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-id")

        recipe_list_serialized = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, recipe_list_serialized.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipe is limited to auth user"""
        other_user = create_user(
            email="other@mail.com",
            password="password",
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)

        recipe_list_serialized = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, recipe_list_serialized.data)

    def test_get_recipe_detail(self):
        """test get recipe Details"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        recipe_detail_serialized = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, recipe_detail_serialized.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            "title": "Sample Recipe title 2",
            "time_minutes": 2,
            "price": Decimal("5.99"),
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_patch_recipe(self):
        """Test patch  recipe"""
        original_link = "http://example.com/recipe.png"
        recipe = create_recipe(
            user=self.user,
            title="sample recipe title",
            link=original_link
        )

        payload = {
            "title": "Udpated title"
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_put_recipe(self):
        """Test patch  recipe"""
        original_link = "http://example.com/recipe.png"
        recipe = create_recipe(
            user=self.user,
            title="sample recipe title",
            link=original_link,
            description="Sample description",
        )

        payload = {
            "title": "Udpated title",
            "link": "http://samplenew.com/recipe.png",
            "description": "New recipe description",
            "time_minutes": 10,
            "price": Decimal("2.56")
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_update_user_return_error(self):
        """Test update with other user"""
        other_user = create_user(
            email="other@mail.com",
            password="password",
        )
        recipe = create_recipe(user=self.user)

        payload = {"user": other_user.id}
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test Delete Recipe"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id))

    def test_del_recipe_by_other_user(self):
        """Test delete recipe by ither user"""
        other_user = create_user(
            email="other@mail.com",
            password="password",
        )
        recipe = create_recipe(user=other_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())