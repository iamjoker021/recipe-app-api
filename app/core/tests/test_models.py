"""
Test for Models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_success(self):
        email = "test@example.com"
        password = "password"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

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
            user = get_user_model().objects.create_user(email, 'pass')
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
