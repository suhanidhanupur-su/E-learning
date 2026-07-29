from django.contrib import admin

from .models import Announcement, Category, LiveClass, Course


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


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "start_time", "duration_minutes", "is_active")
    list_filter = ("is_active", "start_time")
    search_fields = ("title", "instructor", "description")
    ordering = ("start_time",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "instructor_name", "price", "is_active", "is_featured", "created_at")
    list_filter = ("is_active", "is_featured", "category")
    search_fields = ("title", "instructor_name", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)
