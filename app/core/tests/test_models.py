"""
Test for Models
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="test@mail.com", password="password"):
    """Create and return Test User"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_success(self):
        email = "test@example.com"
        password = "password"
        user = create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test if email is normalized"""
        sample_email = [
            ('test1@EXAMPLE.com', 'test1@example.com'),
            ('Test2@Example.com', 'Test2@example.com'),
            ('TEST3@EXAMPLE.com', 'TEST3@example.com'),
            ('test4@example.COM', 'test4@example.com'),
        ]
        for email, expected in sample_email:
            user = create_user(email)
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_rases_error(self):
        """Test If Error is rasied if Email not provided"""
        with self.assertRaises(TypeError):
            get_user_model().objects.create_user(password='pass')

    def test_create_superuser(self):
        """Test cretaing Super User"""
        user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="pass"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        user = create_user()
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample Recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description"
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test create tag func"""
        user = create_user()
        tag_name = "Tag1"
        tag = models.Tag.objects.create(user=user, name=tag_name)

        self.assertEqual(str(tag), tag_name)

    def test_create_ingrdient(self):
        """Test Ingrdient create fnc"""
        user = create_user()
        ingrdient_name = "Ingrdient 1"
        ingrdient = models.Ingredient.objects.create(
            user=user,
            name=ingrdient_name
        )

        self.assertEqual(str(ingrdient), ingrdient_name)
