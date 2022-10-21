from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status

import pytest

CREATE_USER_URL = reverse("user:create")


def create_user(**params):
    """
    Create and return a new user
    """
    return get_user_model().objects.create_user(**params)


@pytest.mark.django_db
class PublicationApiTests():
    """Test public feauture of user API"""
    pytestmark = pytest.mark.django_db

    def test_create_user_success(self, client):
        payload = {
            "email": "test@mail.com",
            "password": "password",
            "name": "test Name",
        }
        res = client.post(CREATE_USER_URL, payload)

        assert res.status_code == status.HTTP_201_CREATED
        user = get_user_model().objects.get(email=payload["email"])
        assert user.check_password(payload["password"])
        assert "password" not in res.data

    def test_user_with_email_exist_error(self, client):
        payload = {
            "email": "test@mail.com",
            "password": "password",
            "name": "test Name",
        }
        create_user(**payload)

        res = client.post(CREATE_USER_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_too_short_error(self, client):
        payload = {
            "email": "test@mail.com",
            "password": "pass",
            "name": "test Name",
        }
        res = client.post(CREATE_USER_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        assert not user_exists
