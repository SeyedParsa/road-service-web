from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import RedirectView

from reporting import views

app_name = 'reporting'
urlpatterns = [
    path('timereport/', views.TimeReport.as_view()),
    path('statusreport/', views.StatusReport.as_view()),
    url('reports/', RedirectView.as_view(url='/timereport/', permanent=False), name='reports')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)