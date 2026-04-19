from django.contrib.auth.models import User
from django.db import models


class Video(models.Model):
    owner = models.ForeignKey(User, related_name='videos', on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    name = models.CharField(max_length=100, db_index=True)
    total_likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.name


class VideoFile(models.Model):
    QUALITY_CHOICES = (
        ('HD', 'HD'),
        ('FHD', 'FHD'),
        ('UHD', 'UHD'),
    )

    video = models.ForeignKey(Video, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='videos/')
    quality = models.CharField(choices=QUALITY_CHOICES, default='HD', max_length=3)

    def __str__(self):
        return f'{self.video.name} ({self.quality})'

class Like(models.Model):
    video = models.ForeignKey(Video, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['video', 'user'], name='unique_video_user_like')
        ]

    def __str__(self):
        return f'{self.video.name} ({self.user.username})'
