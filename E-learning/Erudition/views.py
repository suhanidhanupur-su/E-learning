import json
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileUpdateForm
from .models import LiveClass, Profile, Category, Course, Enrollment, Enquiry, TeamMember
from django.db.models import Prefetch
from django.contrib.auth import login as auth_login
from django.urls import reverse
from django.http import JsonResponse
from .forms import ProfileUpdateForm, RegisterForm


def home(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]
    return render(request, 'Erudition/home.html', {'featured_courses': featured_courses})


def submit_enquiry(request):
    if request.method != 'POST':
        return JsonResponse({'errors': {'detail': 'Invalid request method.'}}, status=405)

    if request.content_type and 'application/json' in request.content_type:
        try:
            data = request.body.decode('utf-8')
            data = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = {}
    else:
        data = request.POST

    errors = {}

    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()

    if not name:
        errors['name'] = 'Name is required.'
    if not phone:
        errors['phone'] = 'Phone number is required.'
    if not email or '@' not in email:
        errors['email'] = 'Enter a valid email address.'
    if not message:
        errors['message'] = 'Message is required.'

    if errors:
        return JsonResponse({'errors': errors}, status=400)

    Enquiry.objects.create(name=name, phone=phone, email=email, message=message)
    return JsonResponse({'success': True, 'message': 'Thank you! We will get back to you shortly.'})


def about(request):
    team_members = TeamMember.objects.filter(is_active=True).order_by('display_order', 'employee_name')
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]
    return render(request, 'Erudition/about.html', {
        'page_title': 'About Us',
        'page_subtitle': 'Discover our premium corporate and educational learning experiences designed for teams, leaders, and institutions.',
        'team_members': team_members,
        'featured_courses': featured_courses,
    })


def courses(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.order_by('name')
    courses = Course.objects.filter(is_active=True)

    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    courses = courses.order_by('-is_featured', '-created_at')

    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/courses.html', {
        'categories': categories,
        'courses': courses,
        'active_category_slug': category_slug,
        'page_title': 'Courses',
        'page_subtitle': 'Browse our curated collection of skills, certifications, and live training offerings built for modern professionals.',
        'featured_courses': featured_courses,
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    related_courses = Course.objects.filter(category=course.category, is_active=True).exclude(pk=course.pk)[:3]
    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    context = {
        'course': course,
        'related_courses': related_courses,
        'is_enrolled': is_enrolled,
        'what_you_learn': [
            'Understand the foundations of the subject with structured, step-by-step guidance.',
            'Apply practical strategies you can use immediately in your work or studies.',
            'Build confidence through guided exercises and real-world scenarios.',
        ],
        'requirements': [
            'Basic familiarity with the topic is helpful but not required.',
            'A stable internet connection and a reliable device for online learning.',
            'A willingness to practice and engage with the lessons.',
        ],
        'curriculum': [
            {'title': 'Module 1: Foundations', 'description': 'Discover the core ideas, methods, and frameworks that shape the course.'},
            {'title': 'Module 2: Applied Learning', 'description': 'Work through practical assignments and case-based examples.'},
            {'title': 'Module 3: Advanced Practice', 'description': 'Build confidence with guided reflection and next-step planning.'},
        ],
        'page_title': course.title,
        'page_subtitle': course.short_description or course.description,
    }
    return render(request, 'Erudition/course_detail.html', context)


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    if not request.user.is_authenticated:
        next_url = reverse('course_detail', args=[course.slug])
        return redirect(f"{reverse('login')}?next={quote(next_url)}")

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'status': 'approved', 'payment_status': 'pending'},
    )

    if not created:
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('course_detail', slug=course.slug)

    request.session['enrollment_success_slug'] = course.slug
    messages.success(request, 'You have successfully enrolled in this course.')
    return redirect('enrollment_success')


@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course').order_by('-enrolled_at')
    return render(request, 'Erudition/my_courses.html', {
        'enrollments': enrollments,
        'page_title': 'My Courses',
        'page_subtitle': 'Continue learning from your enrolled programs and stay on track with your growth.',
    })


@login_required
def enrollment_success(request):
    slug = request.session.pop('enrollment_success_slug', None)
    course = None

    if slug:
        course = get_object_or_404(Course, slug=slug, is_active=True)
    else:
        latest_enrollment = Enrollment.objects.filter(user=request.user).order_by('-enrolled_at').first()
        if latest_enrollment:
            course = latest_enrollment.course

    if not course:
        return redirect('courses')

    return render(request, 'Erudition/enrollment_success.html', {
        'course': course,
        'page_title': 'Enrollment Success',
        'page_subtitle': 'Your learning journey is ready to begin.',
    })


def live_classes(request):
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '')
    categories = Category.objects.order_by('name')
    live_classes = LiveClass.objects.filter(is_active=True)

    if category_slug:
        live_classes = live_classes.filter(category__slug=category_slug)

    live_classes = live_classes.order_by('start_time')
    live_classes_count = live_classes.count()
    categories_count = categories.count()
    featured_class = live_classes.first()

    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/live_classes.html', {
        'categories': categories,
        'categories_count': categories_count,
        'featured_class': featured_class,
        'live_classes': live_classes,
        'live_classes_count': live_classes_count,
        'active_category_slug': category_slug,
        'search_query': search_query,
        'page_title': 'Live Classes',
        'page_subtitle': 'Join our upcoming live sessions with expert instructors and practical learning experiences.',
        'featured_courses': featured_courses,
    })


def articles(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.order_by('name')

    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/articles.html', {
        'categories': categories,
        'active_category_slug': category_slug,
        'page_title': 'Articles',
        'page_subtitle': 'Explore thought leadership and practical business insights aligned with our learning programs.',
        'featured_courses': featured_courses,
    })


def privacy_policy(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/privacy_policy.html', {
        'page_title': 'Privacy Policy',
        'page_subtitle': 'How we protect your information and maintain trust in every learning engagement.',
        'featured_courses': featured_courses,
    })


def refund_policy(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/refund_policy.html', {
        'page_title': 'Refund Policy',
        'page_subtitle': 'Transparent guidance on enrollment changes, cancellations, and service adjustments.',
        'featured_courses': featured_courses,
    })


def terms_conditions(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/terms_conditions.html', {
        'page_title': 'Terms & Conditions',
        'page_subtitle': 'The standards that shape our partnership, service delivery, and client engagement.',
        'featured_courses': featured_courses,
    })


def our_mission(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/our_mission.html', {
        'page_title': 'Our Mission',
        'page_subtitle': 'A clear commitment to meaningful growth, leadership excellence, and premium learning impact.',
        'featured_courses': featured_courses,
    })


def our_vision(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/our_vision.html', {
        'page_title': 'Our Vision',
        'page_subtitle': 'Building a future where organizations thrive through thoughtful education and strategic transformation.',
        'featured_courses': featured_courses,
    })


def get_or_create_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile


@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/profile.html', {
        'profile': profile,
        'page_title': 'My Profile',
        'page_subtitle': 'Manage your personal details and professional presence.',
        'featured_courses': featured_courses,
    })


@login_required
def edit_profile(request):
    profile = get_or_create_profile(request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            full_name = form.cleaned_data['full_name'].strip()
            names = full_name.split(maxsplit=1)
            request.user.first_name = names[0] if names else ''
            request.user.last_name = names[1] if len(names) > 1 else ''
            request.user.email = form.cleaned_data['email']
            request.user.save(update_fields=['first_name', 'last_name', 'email'])

            profile.full_name = full_name
            profile.phone_number = form.cleaned_data['phone_number']
            if form.cleaned_data.get('profile_photo'):
                profile.profile_photo = form.cleaned_data['profile_photo']
            profile.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(initial={
            'full_name': profile.full_name or f"{request.user.first_name} {request.user.last_name}".strip(),
            'email': request.user.email,
            'phone_number': profile.phone_number,
        }, user=request.user)

    return render(request, 'Erudition/edit_profile.html', {
        'form': form,
        'profile': profile,
        'page_title': 'Edit Profile',
        'page_subtitle': 'Update your contact details and professional photo.',
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Welcome to Erudition! Your account has been created.')
            return redirect('profile')
    else:
        form = RegisterForm()

    return render(request, 'Erudition/register.html', {
        'form': form,
        'page_title': 'Register',
        'page_subtitle': 'Create your account and start your learning journey with Erudition.',
    })
