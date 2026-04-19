import pytest
from rest_framework.test import APIClient

from videoapi.models import Video


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username="john",
        password="12345"
    )


@pytest.fixture
def another_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username="kate",
        password="12345"
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def another_auth_client(another_user):
    client = APIClient()
    client.force_authenticate(user=another_user)
    return client


@pytest.fixture
def published_video(user):
    return Video.objects.create(
        owner=user,
        name="Video 1",
        is_published=True
    )


@pytest.fixture
def private_video(user):
    return Video.objects.create(
        owner=user,
        name="Private",
        is_published=False
    )
