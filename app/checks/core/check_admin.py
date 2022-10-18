"""
Test Django Admin
"""
from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest


@pytest.fixture
@pytest.mark.django_db
def set_up(client):
    client = client
    admin_user = get_user_model().objects.create_superuser(
        email="admin@mail.com",
        password="password"
    )
    client.force_login(admin_user)
    user = get_user_model().objects.create_user(
        email="test@mail.com",
        password="password",
        name="TestUser"
    )
    return user


@pytest.mark.django_db
def test_user_list(set_up, client):
    user = set_up
    url = reverse("admin:core_user_changelist")
    res = client.get(url)

    assert user.name in str(res.content)
    assert user.email in str(res.content)


@pytest.mark.django_db
def test_edit_user_page(set_up, client):
    user = set_up
    url = reverse("admin:core_user_change", args=[user.id])
    res = client.get(url)

    assert res.status_code == 200


@pytest.mark.django_db
def test_create_user_page(client, set_up):
    url = reverse("admin:core_user_add")
    res = client.get(url)

    assert res.status_code == 200
