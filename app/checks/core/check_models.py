"""
Test for Models
"""
import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db(True)
class ModelTests():

    def test_create_user_with_email_success(self):
        email = "test@example.com"
        password = "password"
        user = get_user_model()
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

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
            user = get_user_model().objects.create_user(email, 'pass')
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
