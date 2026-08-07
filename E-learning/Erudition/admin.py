from django.contrib import admin
from django.utils.html import format_html

from .models import Announcement, Category, LiveClass, Course, Enrollment, TeamMember


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
    list_display = ("title", "category", "instructor", "start_time", "duration_minutes", "is_active")
    list_filter = ("is_active", "start_time", "category")
    search_fields = ("title", "instructor", "description")
    ordering = ("start_time",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "instructor_name", "price", "is_active", "is_featured", "created_at")
    list_filter = ("is_active", "is_featured", "category")
    search_fields = ("title", "instructor_name", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "payment_status", "enrolled_at")
    list_filter = ("status", "payment_status")
    search_fields = ("user__username", "course__title")
    ordering = ("-enrolled_at",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    def employee_image_thumbnail(self, obj):
        if obj.employee_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:6px;" />', obj.employee_image.url)
        return "-"

    employee_image_thumbnail.short_description = "Image"

    list_display = ("employee_image_thumbnail", "employee_name", "role")
    search_fields = ("employee_name", "role")
    ordering = ("employee_name",)
    list_per_page = 10
