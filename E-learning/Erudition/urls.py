from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('enroll/<slug:slug>/', views.enroll_course, name='enroll_course'),
    path('checkout/verify/', views.verify_payment, name='verify_payment'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('enrollment-success/', views.enrollment_success, name='enrollment_success'),
    path('articles/', views.articles, name='articles'),
    path('live-classes/', views.live_classes, name='live_classes'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('our-mission/', views.our_mission, name='our_mission'),
    path('our-vision/', views.our_vision, name='our_vision'),
    path('register/', views.register, name='register'),
    path('enquiries/', views.submit_enquiry, name='submit_enquiry'),
]
