from django.conf.urls import url
from django.urls import path
from django.views.generic.base import RedirectView

from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('logout/', views.Logout.as_view()),
    path('signup/', views.Signup.as_view()),
    path('login/', views.Login.as_view()),
    path('password/reset/', views.PasswordReset.as_view()),
    path('password/set/', views.PasswordSet.as_view()),
]
