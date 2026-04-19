import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import Count
from faker import Faker

from videoapi.models import Video, Like


class Command(BaseCommand):
    help = "Generates random data"

    def handle(self, users=10_000, videos=100_000, *args, **options):

        self.stdout.write(self.style.SUCCESS("Generating users..."))
        self.create_users(users)

        self.stdout.write(self.style.SUCCESS("Generating videos..."))
        self.create_videos(videos)

        self.stdout.write(self.style.SUCCESS("Generating likes..."))
        self.create_likes()

        self.stdout.write(
            self.style.SUCCESS("Seed completed successfully.")
        )

    def create_users(self, users_cnt):
        if User.objects.exists():
            return
        users = [
            User(username=f'user_{i}')
            for i in range(users_cnt)
        ]
        User.objects.bulk_create(users, batch_size=1000)

    def create_videos(self, videos_cnt):
        fake = Faker()
        if Video.objects.exists():
            return

        user_ids = list(
            User.objects.values_list("id", flat=True)
        )

        videos = []

        for _ in range(videos_cnt):
            videos.append(
                Video(
                    owner_id=random.choice(user_ids),
                    name=fake.sentence(nb_words=5),
                    is_published=True,
                )
            )

        Video.objects.bulk_create(videos, batch_size=5000)

    def create_likes(self):
        if Like.objects.exists():
            return

        videos = list(
            Video.objects.values("id", "owner_id")
        )

        user_ids = list(
            User.objects.values_list("id", flat=True)
        )

        likes_batch = []
        batch_size = 5000

        for video in videos:
            roll = random.random()

            if roll < 0.7:
                likes_count = random.randint(0, 5)
            elif roll < 0.9:
                likes_count = random.randint(6, 30)
            else:
                likes_count = random.randint(31, 150)

            candidates = [
                uid for uid in user_ids
                if uid != video["owner_id"]
            ]

            likes_count = min(likes_count, len(candidates))

            selected = random.sample(candidates, likes_count)

            for user_id in selected:
                likes_batch.append(
                    Like(
                        video_id=video["id"],
                        user_id=user_id
                    )
                )

            if len(likes_batch) >= batch_size:
                Like.objects.bulk_create(
                    likes_batch,
                    batch_size=batch_size,
                    ignore_conflicts=True
                )
                likes_batch = []

        if likes_batch:
            Like.objects.bulk_create(
                likes_batch,
                batch_size=batch_size,
                ignore_conflicts=True
            )

        self.update_total_likes()

    def update_total_likes(self):
        stats = dict(
            Like.objects.values_list("video_id")
            .annotate(cnt=Count("id"))
        )

        videos = list(Video.objects.only("id"))

        for video in videos:
            video.total_likes = stats.get(video.id, 0)

        Video.objects.bulk_update(
            videos,
            ["total_likes"],
            batch_size=5000
        )
