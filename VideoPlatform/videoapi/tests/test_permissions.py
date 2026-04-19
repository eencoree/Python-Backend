import pytest


@pytest.mark.django_db
def test_get_published_video(published_video, auth_client):
    response = auth_client.get(f'/v1/videos/{published_video.id}/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_private_video_forbidden(private_video, another_auth_client):
    response = another_auth_client.get(f"/v1/videos/{private_video.id}/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_private_video_owner_allowed(private_video, auth_client):
    response = auth_client.get(f"/v1/videos/{private_video.id}/")

    assert response.status_code == 200
