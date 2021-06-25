from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from accounts.forms import SignUpForm


class Logout(View):
    def get(self, request):
        logout(request)
        messages.success(request, "شما با موفقیت از اکانت خود خارج شدید")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class Signup(View):
    def get(self, request):
        form = SignUpForm()
        return render(request=request,
                      template_name='accounts/signup.html',
                      context={'form': form})

    def post(self, request):
        messages.success(request, "شما با موافقیت ثبت‌نام شدید!")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class Login(View):
    def get(self, request):
        return render(request=request,
                      template_name='accounts/login.html')

    def post(self, request):
        messages.success(request, "شما با موافقیت وارد شدید!")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class PasswordReset(View):
    def get(self, request):
        return render(request=request,
                      template_name='accounts/resetpassword.html')

    def post(self, request):
        messages.success(request, "لینک بازیابی گذرواژه برای شما پیامک شد!")
        return render(request=request,
                      template_name='accounts/resetpassword.html')


class PasswordSet(View):
    def get(self, request):
        return render(request=request,
                      template_name='accounts/setnewpassword.html')

    def post(self, request):
        messages.success(request, "گذرواژه جدید شما با موفقیت ذخیره شد!")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
