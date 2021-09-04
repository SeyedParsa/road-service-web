from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

import core.views
from accounts import views, api_views

app_name = 'accounts'
urlpatterns = [
    path('api/user/', api_views.UserView.as_view()),
    path('api/change-password/', api_views.ChangePasswordView.as_view()),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/setnewpassword.html',
                                                     success_url=reverse_lazy('accounts:password_reset_complete')),
         name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),

    path('logout/', views.Logout.as_view()),
    path('login/', views.Login.as_view(), name='login'),
    path('password/reset/', views.PasswordReset.as_view()),
    path('password/set/', views.PasswordSet.as_view()),
]
