import django.contrib.auth.admin
from django.contrib import admin

from accounts.forms import UserCreationForm, UserChangeForm
from accounts.models import User, Role


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    fieldsets = django.contrib.auth.admin.UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )
    add_fieldsets = django.contrib.auth.admin.UserAdmin.add_fieldsets + (
        (None, {'fields': ('first_name', 'last_name', 'phone_number',)}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Role)
