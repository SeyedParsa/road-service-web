from django.urls import path
from django.views.generic.base import RedirectView

from core import views, api_views

app_name = 'core'
urlpatterns = [
    path('api/signup/', api_views.SignUpView.as_view()),
    path('api/regions/', api_views.RegionsListView.as_view()),
    path('api/specialities/', api_views.SpecialitiesView.as_view()),
    path('api/machinery-types/', api_views.MachineryTypesView.as_view()),
    path('api/mission-types/', api_views.MissionTypesView.as_view()),
    path('api/citizen/issue/', api_views.CurrentIssueView.as_view()),
    path('api/citizen/report-issue/', api_views.ReportIssueView.as_view()),
    path('api/citizen/rate-issue/', api_views.RateIssueView.as_view()),
    path('api/serviceman/location/', api_views.ServicemanLocationView.as_view()),
    path('api/serviceman/team/', api_views.ServiceTeamView.as_view()),
    path('api/serviceman/mission/', api_views.CurrentMissionView.as_view()),
    path('api/serviceman/update-location/', api_views.UpdateLocationView.as_view()),
    path('api/serviceman/finish-mission/', api_views.FinishMissionView.as_view()),
    path('api/expert/issues/', api_views.ReportedIssuesView.as_view()),
    path('api/expert/accept-issue/', api_views.AcceptIssueView.as_view()),
    path('api/expert/reject-issue/', api_views.RejectIssueView.as_view()),

    path('assignmoderator/', views.AssignModerator.as_view()),
    path('dashboard/<int:issue_id>/', views.IssueCard.as_view()),
    path('dashboard/', views.Home.as_view()),
    path('resources/', views.Resources.as_view()),
    path('resources/teamdetails/<int:issue_id>/', views.IssueCard.as_view()),
    path('resources/changeteam/<int:team_id>/', views.ChangeTeam.as_view()),
    path('resources/changemission/<int:mission_id>/', views.ChangeMission.as_view()),
    path('resources/changespeciality/<int:speciality_id>/', views.ChangeSpeciality.as_view()),

    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='dashboard'),
]
