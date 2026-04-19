from django.urls import path, include
from rest_framework import routers

from videoapi.views import VideoViewSet

router = routers.DefaultRouter()
router.register(r'videos', VideoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
