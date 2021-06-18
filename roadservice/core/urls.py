from django.conf.urls import url
from django.urls import path
from django.views.generic.base import RedirectView

from core import views

app_name = 'core'
urlpatterns = [
    path('accept-issue/', views.AcceptIssue.as_view()),
    path('update-location/', views.UpdateLocation.as_view()),
    path('assign-moderator/', views.AssignModerator.as_view()),
    path('home/', views.Home.as_view()),
    path('logout/', views.logmeout)
]
