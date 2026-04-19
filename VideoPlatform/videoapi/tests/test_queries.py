import pytest


@pytest.mark.django_db
def test_video_list_queries(django_assert_num_queries, published_video, auth_client):
    with django_assert_num_queries(2):
        response = auth_client.get("/v1/videos/")
        assert response.status_code == 200

@pytest.mark.django_db
def test_video_list_ids(django_assert_num_queries, published_video, auth_client):
    with django_assert_num_queries(1):
        response = auth_client.get("/v1/videos/ids/")
        assert response.status_code == 200


@pytest.mark.django_db
def test_statistics_subquery_queries(django_assert_num_queries, auth_client):
    with django_assert_num_queries(1):
        response = auth_client.get("/v1/videos/statistics-subquery/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_statistics_group_by_queries(django_assert_num_queries, auth_client):
    with django_assert_num_queries(1):
        response = auth_client.get("/v1/videos/statistics-group-by/")

    assert response.status_code == 200
