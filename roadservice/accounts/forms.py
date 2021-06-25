from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import password_validators_help_texts
from django.utils.html import format_html

from accounts.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='اختیاری', label="نام")
    last_name = forms.CharField(max_length=30, required=False, help_text='اختیاری', label="نام خانوادگی")
    id_number = forms.CharField(max_length=15, required=True, help_text="وارد کردن کد ملی صحیح لازم است.", label="کد ملی")
    phone_number = forms.CharField(max_length=30, required=False, help_text="اختیاری", label="شماره تماس")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'id_number', 'phone_number', 'password1', 'password2')
