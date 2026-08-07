from .models import Announcement, Course


def active_announcement(request):
    announcement = Announcement.objects.filter(is_active=True).order_by('-created_at').first()
    return {'active_announcement': announcement}


def featured_courses_context(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]
    return {'featured_courses': featured_courses}
