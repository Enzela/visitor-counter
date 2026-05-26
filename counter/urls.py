from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/total/', views.api_total, name='api_total'),
    path('api/log/', views.api_log_visitor, name='api_log'),
    path('api/recent/', views.api_recent, name='api_recent'),
    path('api/all/', views.api_all, name='api_all'),
]