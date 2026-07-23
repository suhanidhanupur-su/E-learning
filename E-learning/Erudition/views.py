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
