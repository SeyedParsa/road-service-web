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
    id_number = forms.CharField(max_length=15, required=True, help_text="وارد کردن کد ملی صحیح لازم است.", label="کد ملی")
    phone_number = forms.CharField(max_length=30, required=False, help_text="اختیاری", label="شماره تماس")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'id_number', 'phone_number', 'password1', 'password2')
