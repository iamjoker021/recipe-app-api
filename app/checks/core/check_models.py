"""
Test for Models
"""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from core import models


def create_user(email="test@mail.com", password="password"):
    """Create and return Test User"""
    return get_user_model().objects.create_user(email=email, password=password)


@pytest.mark.django_db(True)
class ModelTests():

    def test_create_user_with_email_success(self):
        email = "test@mail.com"
        password = "password"
        user = create_user(email=email, password=password)

        assert user.email == email
        assert user.check_password(password)

    def test_new_user_email_normalized(self):
        """Test if email is normalized"""
        sample_email = [
            ('test1@EXAMPLE.com', 'test1@example.com'),
            ('Test2@Example.com', 'Test2@example.com'),
            ('TEST3@EXAMPLE.com', 'TEST3@example.com'),
            ('test4@example.COM', 'test4@example.com'),
        ]
        for email, expected in sample_email:
            user = create_user(email=email)
            assert user.email == expected

    def test_create_user_without_email_raise_error(sled):
        """Test If Error is rasied if Email not provided"""
        with pytest.raises(TypeError) as e:
            get_user_model().objects.create_user(password='pass')
        assert "email" in str(e.value)

    def test_create_superuser(self):
        """Test cretaing Super User"""
        user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="pass"
        )

        assert user.is_superuser
        assert user.is_staff

    def test_create_recipe(self):
        user = create_user()
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample Recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description"
        )

        assert str(recipe) == recipe.title

    def test_create_tag(self):
        """Test create tag func"""
        user = create_user()
        tag_name = "Tag1"
        tag = models.Tag.objects.create(user=user, name=tag_name)

        assert str(tag) == tag_name

    def test_create_ingrdient(self):
        """Test Ingrdient create fnc"""
        user = create_user()
        ingrdient_name = "Ingrdient 1"
        ingrdient = models.Ingredient.objects.create(
            user=user,
            name=ingrdient_name
        )

        assert str(ingrdient) == ingrdient_name

    def test_recipe_file_name_uuild(self, mocker):
        """Test generate image path"""
        uuid = "test_uuid"
        mocker_func = mocker.patch(
            "core.models.uuid.uuid4",
        )
        mocker_func.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpg")

        assert file_path == f"uploads/recipe/{uuid}.jpg"
