from django.conf.urls import url
from django.urls import path
from django.views.generic.base import RedirectView

from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('logout/', views.Logout.as_view())
]
