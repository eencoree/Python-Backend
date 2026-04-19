from django.db import transaction, IntegrityError
from django.db.models import F, OuterRef, Count, Subquery
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from videoapi.models import Video, Like
from videoapi.permissions import CanViewVideo
from videoapi.serializers import VideoListSerializer, VideoDetailSerializer, VideoDetailExpandedSerializer


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.select_related('owner')
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['owner__username', 'name']
    search_fields = ['name']
    ordering_fields = ['created_at', 'owner__username', 'total_likes']

    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer

        if self.action == 'retrieve':
            if self.request.query_params.get('user_expand') == 'true':
                return VideoDetailExpandedSerializer
            return VideoDetailSerializer

        return VideoDetailSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            return [CanViewVideo()]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='likes')
    def like(self, request, pk=None):
        video = self.get_object()

        if video.owner == request.user:
            return Response(
                {"error": "You can't like your own video"},
                status=400
            )

        try:
            with transaction.atomic():
                Like.objects.create(video=video, user=request.user)

                Video.objects.filter(pk=video.pk).update(
                    total_likes=F('total_likes') + 1
                )

        except IntegrityError:
            return Response(
                {"error": "Already liked"},
                status=400
            )

        return Response({"success": True}, status=201)

    @action(detail=False, methods=['get'], url_path='ids')
    def ids(self, request):
        videos = (
            Video.objects
            .filter(is_published=True)
            .values_list('id', flat=True)
        )
        return Response(list(videos), status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='statistics-subquery')
    def statistics_subquery(self, request):
        likes_subquery = (
            Like.objects.filter(
                video=OuterRef('pk')
            )
            .values('video')
            .annotate(cnt=Count('*'))
            .values('cnt')[:1]
        )
        qs = (
            Video.objects
            .annotate(
                likes_count=Coalesce(
                    Subquery(likes_subquery, output_field=IntegerField()), 0
                )
            )
            .values('id', 'likes_count')
        )
        data = qs.values('id', total_likes=F('likes_count'))
        return Response(list(data), status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='statistics-group-by')
    def statistics_group_by(self, request):
        data = (
            Video.objects
            .values('id')
            .annotate(total_likes=Count('likes'))
            .order_by('id')
        )

        return Response(list(data), status=HTTP_200_OK)
