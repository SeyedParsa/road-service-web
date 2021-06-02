from django.urls import path

from reporting import views

app_name = 'reporting'
urlpatterns = [
    path('timereports/', views.TimeReportView.as_view()),
]
