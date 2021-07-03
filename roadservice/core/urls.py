from django.conf.urls import url
from django.urls import path
from django.views.generic.base import RedirectView

from core import views

app_name = 'core'
urlpatterns = [
    path('accept-issue/', views.AcceptIssue.as_view()),
    path('update-location/', views.UpdateLocation.as_view()),
    path('assign-moderator/', views.AssignModerator.as_view()),
    path('dashboard/<int:issue_id>/', views.IssueCard.as_view()),
    path('dashboard/', views.Home.as_view()),
    path('resources/', views.ResourcesView.as_view()),
    path('resources/teamdetails/<int:issue_id>/', views.IssueCard.as_view()),
    path('resources/changeteam/<int:team_id>/', views.ChangeTeam.as_view()),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='dashboard'),
]
