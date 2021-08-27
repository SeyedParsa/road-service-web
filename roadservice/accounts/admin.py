import django.contrib.auth.admin
from django.contrib import admin

from accounts.forms import UserCreationForm, UserChangeForm
from accounts.models import User, Role


@admin.register(User)
class UserAdmin(django.contrib.auth.admin.UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User


admin.site.register(Role)
