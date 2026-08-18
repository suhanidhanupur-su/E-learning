import json
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest

import razorpay

from .forms import ProfileUpdateForm, RegisterForm
from .models import Article, LiveClass, Profile, Category, Course, Enrollment, Enquiry, TeamMember


def home(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]
    live_classes = LiveClass.objects.filter(is_active=True).order_by('start_time')[:2]

    latest_articles = []
    if Article is not None:
        latest_articles = Article.objects.order_by('-published_at')[:3]
    else:
        latest_articles = [
            {
                'title': '5 Habits That Separate Good Managers From Great Leaders',
                'category': 'Leadership',
                'excerpt': 'Leadership is a set of daily habits, not a title. Discover the five habits that turn ordinary managers into trusted leaders.',
                'author': 'Erudition Team',
                'read_time': '5 min read',
                'image': '',
            },
            {
                'title': 'How to Speak With Confidence in Any Situation',
                'category': 'Communication',
                'excerpt': 'From boardroom conversations to difficult feedback, these practical techniques help professionals communicate clearly and confidently.',
                'author': 'Erudition Team',
                'read_time': '4 min read',
                'image': '',
            },
            {
                'title': 'Why Soft Skills Are the New Hard Skills in 2025',
                'category': 'Career Growth',
                'excerpt': 'Technical expertise helps you get hired, but soft skills help you stay relevant, lead teams, and grow in the real world.',
                'author': 'Erudition Team',
                'read_time': '6 min read',
                'image': '',
            },
        ]

    return render(request, 'Erudition/home.html', {
        'featured_courses': featured_courses,
        'live_classes': live_classes,
        'latest_articles': latest_articles,
    })


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

    if course.price == 0:
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': 'paid', 'payment_status': 'completed'},
        )
        if not created and enrollment.payment_status != 'completed':
            enrollment.payment_status = 'completed'
            enrollment.status = 'paid'
            enrollment.save(update_fields=['payment_status', 'status'])
        request.session['enrollment_success_slug'] = course.slug
        messages.success(request, 'You have successfully enrolled in this course.')
        return redirect('enrollment_success')

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, 'Payment configuration is missing. Please contact support.')
        return redirect('course_detail', slug=course.slug)

    existing_enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if existing_enrollment and existing_enrollment.payment_status == 'completed':
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('course_detail', slug=course.slug)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_paise = int(course.price * 100)

    razorpay_order = client.order.create({
        'amount': amount_paise,
        'currency': settings.RAZORPAY_CURRENCY,
        'receipt': f'course_{course.id}_user_{request.user.id}',
        'payment_capture': 1,
    })

    enrollment, _ = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'status': 'approved', 'payment_status': 'pending', 'razorpay_order_id': razorpay_order.get('id')},
    )
    if enrollment.razorpay_order_id != razorpay_order.get('id'):
        enrollment.razorpay_order_id = razorpay_order.get('id')
        enrollment.payment_status = 'pending'
        enrollment.save(update_fields=['razorpay_order_id', 'payment_status'])

    return render(request, 'Erudition/checkout.html', {
        'course': course,
        'enrollment': enrollment,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order': razorpay_order,
        'user': request.user,
        'amount': amount_paise,
        'currency': settings.RAZORPAY_CURRENCY,
    })


@login_required
def verify_payment(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method.')

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse({'error': 'Payment configuration is missing.'}, status=500)

    payment_id = request.POST.get('razorpay_payment_id')
    order_id = request.POST.get('razorpay_order_id')
    signature = request.POST.get('razorpay_signature')
    course_slug = request.POST.get('course_slug')

    if not payment_id or not order_id or not signature or not course_slug:
        return JsonResponse({'error': 'Missing payment details.'}, status=400)

    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course, razorpay_order_id=order_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
    except razorpay.errors.SignatureVerificationError:
        enrollment.payment_status = 'failed'
        enrollment.save(update_fields=['payment_status'])
        return JsonResponse({'error': 'Payment signature verification failed.'}, status=400)

    enrollment.payment_status = 'completed'
    enrollment.razorpay_payment_id = payment_id
    enrollment.status = 'paid'
    enrollment.save(update_fields=['payment_status', 'razorpay_payment_id', 'status'])

    request.session['enrollment_success_slug'] = course.slug
    return JsonResponse({'success': True, 'redirect_url': reverse('enrollment_success')})


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
    articles = Article.objects.filter(is_published=True).order_by('-published_at')

    if category_slug and category_slug != 'all':
        articles = articles.filter(category__iexact=category_slug)

    if not articles.exists():
        articles = [
            {
                'title': '5 Habits That Separate Good Managers From Great Leaders',
                'slug': '5-habits-that-separate-good-managers-from-great-leaders',
                'category': 'Leadership',
                'excerpt': 'Leadership is a set of daily habits. Discover the five behaviours that transform managers into leaders others want to follow.',
                'author': 'Erudition Team',
                'read_time': '5 min read',
            },
            {
                'title': 'How to Speak With Confidence in Any Situation',
                'slug': 'how-to-speak-with-confidence-in-any-situation',
                'category': 'Communication',
                'excerpt': 'Whether it is a boardroom presentation or a difficult conversation, these techniques help you speak clearly and confidently.',
                'author': 'Erudition Team',
                'read_time': '4 min read',
            },
            {
                'title': 'Why Soft Skills Are the New Hard Skills in 2025',
                'slug': 'why-soft-skills-are-the-new-hard-skills-in-2025',
                'category': 'Career Growth',
                'excerpt': 'Technical expertise helps you get hired, but soft skills help you lead, adapt and stay relevant in a changing world.',
                'author': 'Erudition Team',
                'read_time': '6 min read',
            },
        ]

    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/articles.html', {
        'categories': categories,
        'articles': articles,
        'active_category_slug': category_slug,
        'page_title': 'Articles',
        'page_subtitle': 'Explore thought leadership and practical business insights aligned with our learning programs.',
        'featured_courses': featured_courses,
    })


def article_detail(request, slug):
    article = Article.objects.filter(slug=slug, is_published=True).first()

    if article is None:
        fallback = {
            'title': slug.replace('-', ' ').title(),
            'slug': slug,
            'category': 'Leadership',
            'excerpt': 'Thought leadership, learning strategies and practical insights for modern professionals.',
            'content': 'This article detail page is available for the homepage article links. Use the existing article model and add real content when your editorial content is ready.',
            'author': 'Erudition Team',
            'read_time': '5 min read',
            'published_at': None,
        }
        article = fallback

    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'Erudition/article_detail.html', {
        'article': article,
        'page_title': article['title'] if isinstance(article, dict) else article.title,
        'page_subtitle': article['excerpt'] if isinstance(article, dict) else article.excerpt or 'Read more from Erudition.',
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
