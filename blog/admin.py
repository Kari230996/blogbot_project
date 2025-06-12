from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content", "owner", "created_at")
    search_fields = ("title", "content", "owner__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
