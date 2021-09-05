import django.contrib.auth.forms
from django import forms

from accounts.models import User


class UserCreationForm(django.contrib.auth.forms.UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'phone_number')


class UserChangeForm(django.contrib.auth.forms.UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'phone_number')


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='اختیاری', label="نام")
    last_name = forms.CharField(max_length=30, required=False, help_text='اختیاری', label="نام خانوادگی")
    phone_number = forms.CharField(max_length=30, required=False, help_text="اجباری", label="شماره تماس")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'password1', 'password2')


class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=30, required=False, help_text="اجباری", label="شماره تماس")
    password = forms.CharField(max_length=30, required=False, help_text="اجباری", label="گذرواژه")


class PasswordResetForm(forms.Form):
    phone_number = forms.CharField(max_length=30, required=False, help_text="اجباری", label="شماره تماس")


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
