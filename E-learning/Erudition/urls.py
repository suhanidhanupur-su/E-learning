from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('our-mission/', views.our_mission, name='our_mission'),
    path('our-vision/', views.our_vision, name='our_vision'),
]
