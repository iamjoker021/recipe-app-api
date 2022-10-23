"""
Test Ingredient API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Return Ingredient ID URL"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="test@mail.com", password="password"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientAPITests(TestCase):
    """Test UnAuth Ingredient API req"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_req_ingrdient(self):
        """Test auth blovk for ingredient"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test Auth Ingreient api req"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredient(self):
        """Test get all ingredient"""
        Ingredient.objects.create(user=self.user, name="kale")
        Ingredient.objects.create(user=self.user, name="vanilla")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_retrive_ingredient_only_to_correct_user(self):
        """Test get ingredient only for correct auth user"""
        new_user = create_user(email="test2@mail.com")
        Ingredient.objects.create(user=new_user, name="kale")
        ingredient = Ingredient.objects.create(user=self.user, name="vanilla")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        """Test update INgredient"""
        ingredient = Ingredient.objects.create(user=self.user, name="vanilla")

        payload = {"name": "Coriandor"}

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test delete ingrdient"""
        ingredient = Ingredient.objects.create(user=self.user, name="vanilla")

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredients_exists = Ingredient.objects.filter(user=self.user).exists()

        self.assertFalse(ingredients_exists)
