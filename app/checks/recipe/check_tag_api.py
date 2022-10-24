"""
Test Tag API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe,
)

from recipe.serializers import TagSerializer

import pytest


TAGS_URL = reverse("recipe:tag-list")


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


def detail_url(tag_id):
    """Cerate and return tag detail url"""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="test@mail.com", password="password"):
    """Create and return Test User"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagAPITests():
    """Test UnAuth Tag APi req"""

    @pytest.fixture
    def set_up(self):
        self.client = APIClient()

    def test_auth_required(self, set_up):
        """Test auth is req for retrice tags"""
        res = self.client.get(TAGS_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db(True)
class ProvateTagApiTests():
    """Test Auth Tag Api req"""

    @pytest.fixture
    def set_up(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tag_list(self, set_up):
        """Test Tag list retrived"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_retrive_user_only_tag(self, set_up):
        """Test if user created tags only returned"""
        new_user = create_user(email="test2@mail.com")

        Tag.objects.create(user=new_user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_update_tag_detail(self, set_up):
        """Test update tag func"""
        tag = Tag.objects.create(user=self.user, name="dinner")

        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        assert res.status_code == status.HTTP_200_OK

        tag.refresh_from_db()
        assert tag.name == payload["name"]

    def test_delete_tag(self, set_up):
        """Test delete fucn"""
        tag = Tag.objects.create(user=self.user, name="dinner")
        url = detail_url(tag.id)
        res = self.client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT

        assert not Tag.objects.filter(id=tag.id).exists()

    def test_filter_ingrdient_assigned_to_recipe(self, set_up):
        """Test list ingredieent to those assigned to Recipes"""
        tag1 = Tag.objects.create(user=self.user, name="tag1")
        tag2 = Tag.objects.create(user=self.user, name="tag2")
        r1 = create_recipe(user=self.user, title="recipe test")
        r1.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        assert res.status_code == status.HTTP_200_OK

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        assert s1.data in res.data
        assert s2.data not in res.data

    def test_filter_tag_unique(self, set_up):
        """Test filtered ing return unique val"""
        tag1 = Tag.objects.create(user=self.user, name="tag1")
        Tag.objects.create(user=self.user, name="tag2")
        r1 = create_recipe(user=self.user, title="recipe1")
        r2 = create_recipe(user=self.user, title="recipe2")
        r1.tags.add(tag1)
        r2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        assert res.status_code == status.HTTP_200_OK

        assert len(res.data) == 1
