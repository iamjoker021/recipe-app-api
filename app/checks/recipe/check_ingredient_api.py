"""
Test Ingredient API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient,
    Recipe,
)

from recipe.serializers import IngredientSerializer

import pytest


INGREDIENTS_URL = reverse("recipe:ingredient-list")


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


def detail_url(ingredient_id):
    """Return Ingredient ID URL"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="test@mail.com", password="password"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicRecipeAPITests():
    """Test UnAuth Ingredient API req"""

    @pytest.fixture
    def set_up(self):
        self.client = APIClient()

    def test_auth_req_ingrdient(self, set_up):
        """Test auth blovk for ingredient"""
        res = self.client.get(INGREDIENTS_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db(True)
class PrivateIngredientAPITests():
    """Test Auth Ingreient api req"""

    @pytest.fixture
    def set_up(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredient(self, set_up):
        """Test get all ingredient"""
        Ingredient.objects.create(user=self.user, name="kale")
        Ingredient.objects.create(user=self.user, name="vanilla")

        res = self.client.get(INGREDIENTS_URL)

        assert res.status_code == status.HTTP_200_OK

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        assert res.data == serializer.data

    def test_retrive_ingredient_only_to_correct_user(self, set_up):
        """Test get ingredient only for correct auth user"""
        new_user = create_user(email="test2@mail.com")
        Ingredient.objects.create(user=new_user, name="kale")
        ingredient = Ingredient.objects.create(user=self.user, name="vanilla")

        res = self.client.get(INGREDIENTS_URL)

        assert res.status_code == status.HTTP_200_OK

        assert len(res.data) == 1
        assert res.data[0]["name"] == ingredient.name
        assert res.data[0]["id"] == ingredient.id

    def test_update_ingredient(self, set_up):
        """Test update INgredient"""
        ingredient = Ingredient.objects.create(user=self.user, name="vanilla")

        payload = {"name": "Coriandor"}

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        assert res.status_code == status.HTTP_200_OK
        ingredient.refresh_from_db()
        assert ingredient.name == payload["name"]

    def test_delete_ingredient(self, set_up):
        """Test delete ingrdient"""
        ingredient = Ingredient.objects.create(user=self.user, name="vanilla")

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT

        ingredients_exists = Ingredient.objects.filter(user=self.user).exists()

        assert not ingredients_exists

    def test_filter_ingrdient_assigned_to_recipe(self, set_up):
        """Test list ingredieent to those assigned to Recipes"""
        ingredient1 = Ingredient.objects.create(user=self.user, name="ing1")
        ingredient2 = Ingredient.objects.create(user=self.user, name="ing2")
        r1 = create_recipe(user=self.user, title="recipe test")
        r1.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        assert res.status_code == status.HTTP_200_OK

        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)

        assert s1.data in res.data
        assert s2.data not in res.data

    def test_filter_ingredient_unique(self, set_up):
        """Test filtered ing return unique val"""
        ing = Ingredient.objects.create(user=self.user, name="ing1")
        Ingredient.objects.create(user=self.user, name="ing2")
        r1 = create_recipe(user=self.user, title="recipe1")
        r2 = create_recipe(user=self.user, title="recipe2")
        r1.ingredients.add(ing)
        r2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        assert res.status_code == status.HTTP_200_OK

        assert len(res.data) == 1
