from django.urls import path

from accounts import views, api_views

app_name = 'accounts'
urlpatterns = [
    path('api/user/', api_views.UserView.as_view()),
    path('api/signup/', api_views.SignUpView.as_view()),

    path('logout/', views.Logout.as_view()),
    path('signup/', views.Signup.as_view()),
    path('login/', views.Login.as_view()),
    path('password/reset/', views.PasswordReset.as_view()),
    path('password/set/', views.PasswordSet.as_view()),
]
