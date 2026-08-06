from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm
from .models import LiveClass, Profile, Category, Course, TeamMember
from django.db.models import Prefetch
from django.contrib.auth import login as auth_login
from .forms import ProfileUpdateForm, RegisterForm


def home(request):
    return render(request, 'Erudition/home.html')


def about(request):
    team_members = TeamMember.objects.filter(is_active=True).order_by('display_order', 'employee_name')
    return render(request, 'Erudition/about.html', {
        'page_title': 'About Us',
        'page_subtitle': 'Discover our premium corporate and educational learning experiences designed for teams, leaders, and institutions.',
        'team_members': team_members,
    })


def courses(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.order_by('name')
    courses = Course.objects.filter(is_active=True)

    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    courses = courses.order_by('-is_featured', '-created_at')

    return render(request, 'Erudition/courses.html', {
        'categories': categories,
        'courses': courses,
        'active_category_slug': category_slug,
        'page_title': 'Courses',
        'page_subtitle': 'Browse our curated collection of skills, certifications, and live training offerings built for modern professionals.',
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
    })


def articles(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.order_by('name')

    return render(request, 'Erudition/articles.html', {
        'categories': categories,
        'active_category_slug': category_slug,
        'page_title': 'Articles',
        'page_subtitle': 'Explore thought leadership and practical business insights aligned with our learning programs.',
    })


def privacy_policy(request):
    return render(request, 'Erudition/privacy_policy.html', {
        'page_title': 'Privacy Policy',
        'page_subtitle': 'How we protect your information and maintain trust in every learning engagement.',
    })


def refund_policy(request):
    return render(request, 'Erudition/refund_policy.html', {
        'page_title': 'Refund Policy',
        'page_subtitle': 'Transparent guidance on enrollment changes, cancellations, and service adjustments.',
    })


def terms_conditions(request):
    return render(request, 'Erudition/terms_conditions.html', {
        'page_title': 'Terms & Conditions',
        'page_subtitle': 'The standards that shape our partnership, service delivery, and client engagement.',
    })


def our_mission(request):
    return render(request, 'Erudition/our_mission.html', {
        'page_title': 'Our Mission',
        'page_subtitle': 'A clear commitment to meaningful growth, leadership excellence, and premium learning impact.',
    })


def our_vision(request):
    return render(request, 'Erudition/our_vision.html', {
        'page_title': 'Our Vision',
        'page_subtitle': 'Building a future where organizations thrive through thoughtful education and strategic transformation.',
    })


def get_or_create_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile


@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)
    return render(request, 'Erudition/profile.html', {
        'profile': profile,
        'page_title': 'My Profile',
        'page_subtitle': 'Manage your personal details and professional presence.',
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
