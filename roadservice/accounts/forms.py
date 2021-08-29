import django.contrib.auth.forms
from django import forms
<<<<<<< 9b69768459a0b83e5bf1fcbc89fc56b2cc0dbb08
=======
from django.contrib.auth import get_user_model, authenticate
>>>>>>> do basis of authentication logic
from django.utils.text import capfirst

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
    # id_number = forms.CharField(max_length=15, required=True, help_text="وارد کردن کد ملی صحیح لازم است.",
    # label="کد ملی")
    phone_number = forms.CharField(max_length=30, required=False, help_text="اختیاری", label="شماره تماس")
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'password1', 'password2')


class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=30, required=False, help_text="اجباری", label="شماره تماس")
    password = forms.CharField(max_length=30, required=False, help_text="اجباری", label="گذرواژه")


class PasswordResetForm(forms.Form):
    phone_number = forms.CharField(max_length=30, required=False, help_text="اجباری", label="شماره تماس")


class NewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())