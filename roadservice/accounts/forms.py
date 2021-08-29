import django.contrib.auth.forms
from django import forms
from django.contrib.auth import get_user_model, authenticate
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


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    phone_number/password logins.
    """
    phone_number = forms.CharField(max_length=30, required=False, help_text="اختیاری", label="شماره تماس")
    password = forms.CharField(label="گذرواژه", widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': "Please enter a correct %(phone_number)s and password. "
                           "Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive.",
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "phone_namber" field.
        UserModel = get_user_model()
        self.phone_number_field = UserModel._meta.get_field(UserModel.PHONENUMBER_FIELD)
        if self.fields['phone_number'].label is None:
            self.fields['phone_number'].label = capfirst(self.phone_number_field.verbose_name)

    def clean(self):
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password')

        if phone_number and password:
            self.user_cache = authenticate(phone_number=phone_number,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'phone_number': self.phone_number_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
