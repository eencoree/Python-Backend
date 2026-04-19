import pytest


@pytest.mark.django_db
def test_like_video(another_auth_client, published_video):
    response = another_auth_client.post(
        f"/v1/videos/{published_video.id}/likes/"
    )

    published_video.refresh_from_db()

    assert response.status_code == 201
    assert published_video.total_likes == 1


@pytest.mark.django_db
def test_like_twice_forbidden(another_auth_client, published_video):
    another_auth_client.post(f"/v1/videos/{published_video.id}/likes/")
    response = another_auth_client.post(f"/v1/videos/{published_video.id}/likes/")

    assert response.status_code == 400


@pytest.mark.django_db
def test_like_own_video_forbidden(auth_client, published_video):
    response = auth_client.post(
        f"/v1/videos/{published_video.id}/likes/"
    )

    assert response.status_code == 400
