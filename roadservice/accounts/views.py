from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render
from django.views import View
from accounts.forms import LoginForm, PasswordResetForm, NewPasswordForm


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
                      template_name='accounts/resetpassword.html', context={'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            messages.success(request, "لینک بازیابی گذرواژه برای شما پیامک شد!")
            # TODO: Send the SMS!
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "فرم متعبر نیست!")
            return render(request=request,
                          template_name='accounts/resetpassword.html', context={'form': form})


class PasswordSet(View):
    def get(self, request):
        # TODO: Check validity of the url
        form = NewPasswordForm()
        return render(request=request,
                      template_name='accounts/setnewpassword.html', context={'form': form})

    def post(self, request):
        # TODO: Check validity of the url
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            messages.success(request, "گذرواژه جدید شما با موفقیت ذخیره شد!")
            # TODO: Reset The Password!
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "فرم متعبر نیست!")
            return render(request=request,
                          template_name='accounts/setnewpassword.html', context={'form': form})
