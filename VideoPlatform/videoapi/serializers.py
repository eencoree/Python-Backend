from django.contrib.auth.models import User
from rest_framework import serializers

from videoapi.models import Video, VideoFile, Like


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class VideoListSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Video
        fields = ('id', 'name', 'created_at', 'owner_id')


class VideoDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class VideoDetailExpandedSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    class Meta:
        model = Video
        fields = '__all__'


class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ('id', 'video', 'file', 'quality')


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'video', 'user')
