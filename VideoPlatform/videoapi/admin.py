from django.contrib import admin

from videoapi.models import VideoFile, Video, Like


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "is_published",
        "total_likes",
        "created_at",
    )

    list_filter = (
        "name",
        "is_published",
        "created_at",
    )

    readonly_fields = (
        "total_likes",
        "created_at",
    )

    date_hierarchy = "created_at"

    search_fields = (
        "name",
        "owner__username",
        "owner__email",
    )

    ordering = ("-created_at",)
    autocomplete_fields = ("owner",)
    list_select_related = ("owner",)


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "video",
        "file",
        "quality",
    )

    list_filter = ("quality",)
    search_fields = ("video__name",)
    autocomplete_fields = ("video",)
    list_select_related = ("video",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "video",
        "user",
    )

    search_fields = (
        "video__name",
        "user__username",
    )

    autocomplete_fields = (
        "video",
        "user",
    )

    list_select_related = (
        "video",
        "user",
    )
