"""
Test Ingredient API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

import pytest


INGREDIENTS_URL = reverse("recipe:ingredient-list")


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
