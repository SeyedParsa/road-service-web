from django.urls import path

from core import views

app_name = 'core'
urlpatterns = [
    path('accept-issue/', views.AcceptIssue.as_view()),
    path('update-location/', views.UpdateLocation.as_view()),
    path('assign-moderator/', views.AssignModerator.as_view()),
]
