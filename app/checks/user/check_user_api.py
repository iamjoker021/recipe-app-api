from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

import pytest

CREATE_USER_URL = reverse("user:create")

TOKEN_URL = reverse("user:token")

ME_URL = reverse("user:me")


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

    def test_create_token_for_user(self, client):
        user_details = {
            "email": "test@mail.com",
            "password": "password",
            "name": "test Name",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }

        res = client.post(TOKEN_URL, payload)

        assert res.status_code == status.HTTP_200_OK

        assert "token" in res.data

    @pytest.mark.parametrize(
        "test_input,",
        [
            ("wrongPass",),
            ("",),
        ]
    )
    def test_bad_password_token_response(self, test_input, client):
        user_details = {
            "email": "test@mail.com",
            "password": "password",
            "name": "test Name",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": test_input,
        }

        res = client.post(TOKEN_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

        assert "token" not in res.data


@pytest.mark.django_db
class PrivateApiTests():
    """Test Authorized test cases"""
    pytestmark = pytest.mark.django_db

    @pytest.fixture
    def set_up(self, client):
        user_details = {
            "email": "test@mail.com",
            "password": "password",
            "name": "test Name",
        }
        self.user = create_user(**user_details)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self, set_up):
        res = self.client.get(ME_URL)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == {
            'name': self.user.name,
            'email': self.user.email,
        }

    def test_post_me_not_allowed(self, set_up):
        res = self.client.post(ME_URL, {})

        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_user_profile(self, set_up):
        payload = {
            "password": "newpassword",
            "name": "udpated test Name",
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        assert self.user.name == payload["name"]
        assert self.user.check_password(payload["password"])
        assert res.status_code == status.HTTP_200_OK
