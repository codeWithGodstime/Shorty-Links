from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.RegistrationView.as_view(), name='signup'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('shorten/', views.shorten, name='shorten'),
    path('', views.HomepageView.as_view(), name='index')
]