from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from accounts.exceptions import WeakPasswordError
from accounts.forms import LoginForm, PasswordResetForm, ChangePasswordForm
from accounts.models import User


class PasswordResetComplete(View):
    def get(self, request):
        messages.success(request, "گذرواژه شما با موافقیت به‌روز شد!")
        return HttpResponseRedirect(reverse('accounts:login'))


class Logout(View):
    def get(self, request):
        logout(request)
        messages.success(request, "شما با موفقیت از اکانت خود خارج شدید!")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        form = LoginForm()
        context = {'form': form}
        return render(request=request,
                      template_name='accounts/login.html', context=context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = authenticate(request, username=phone_number, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "شما با موافقیت وارد شدید!")
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        messages.error(request, "فرم متعبر نیست!")
        return render(request=request,
                      template_name='accounts/login.html', context={'form': form})


class PasswordReset(View):
    def get(self, request):
        form = PasswordResetForm()
        return render(request=request,
                      template_name='accounts/fortgotpassword.html', context={'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            try:
                user = User.objects.get(phone_number=phone_number)
                user.send_reset_password_link()
            except:  # TODO: Check if user exists
                pass
            messages.success(request, "لینک بازیابی گذرواژه برای شما پیامک شد!")
            return HttpResponseRedirect(reverse('accounts:login'))
        else:
            messages.error(request, "فرم متعبر نیست!")
            return render(request=request,
                          template_name='accounts/fortgotpassword.html', context={'form': form})


class ChangePassword(LoginRequiredMixin, View):
    def get(self, request):
        form = ChangePasswordForm()
        return render(request=request,
                      template_name='accounts/changepassword.html', context={'form': form})

    def post(self, request):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_passowrd = form.cleaned_data['old_password']
            correct_password = request.user.check_password(old_passowrd)
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if correct_password and password1 == password2:
                try:
                    request.user.change_password(password1)
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "گذرواژه جدید شما با موفقیت ذخیره شد!")
                    return HttpResponseRedirect(reverse('core:dashboard'))
                except WeakPasswordError:
                    messages.error(request, "گذرواژه ضعیف است!")
        messages.error(request, "فرم متعبر نیست!")
        return render(request=request,
                      template_name='accounts/changepassword.html', context={'form': form})
