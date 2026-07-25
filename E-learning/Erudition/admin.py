from django.contrib import admin

from .models import Announcement, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("message", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("message",)
    ordering = ("-created_at",)
