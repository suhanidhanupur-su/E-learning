from django.shortcuts import render


def home(request):
    return render(request, 'Erudition/home.html')


def about(request):
    return render(request, 'Erudition/about.html', {
        'page_title': 'About Us',
        'page_subtitle': 'Discover our premium corporate and educational learning experiences designed for teams, leaders, and institutions.',
    })


def courses(request):
    return render(request, 'Erudition/courses.html', {
        'page_title': 'Courses',
        'page_subtitle': 'Browse our curated collection of skills, certifications, and live training offerings built for modern professionals.',
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
