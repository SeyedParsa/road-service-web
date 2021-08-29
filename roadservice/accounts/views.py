from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View

from accounts.forms import SignUpForm, AuthenticationForm


class PasswordResetComplete(View):
    def get(self, request):
        messages.success(request, "گذرواژه شما با موافقیت به‌روز شد!")
        return HttpResponseRedirect(reverse('accounts:login'))


class Logout(View):
    def get(self, request):
        logout(request)
        messages.success(request, "شما با موفقیت از اکانت خود خارج شدید!")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class Signup(View):
    def get(self, request):
        # TODO: If logged in, redirect to LOGIN_REDIRECT_URL!
        form = SignUpForm()
        return render(request=request,
                      template_name='accounts/signup.html',
                      context={'form': form})

    def post(self, request):
        # TODO: If logged in, redirect to LOGIN_REDIRECT_URL!
        form = SignUpForm(request.POST)
        if form.is_valid():
            print('VALID FORMMMM!!', form)
            # TODO: Add a new user
            messages.success(request, "کاربر جدید با موافقیت اضافه شد!")
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            # TODO: show specific error
            messages.error(request, "فرم معتبر نیست!")
            return render(request=request,
                          template_name='accounts/signup.html',
                          context={'form': form})


class Login(View):
    def get(self, request):
        # TODO: If logged in, redirect to LOGIN_REDIRECT_URL!
        form = AuthenticationForm()
        context = {'form': form}
        return render(request=request,
                      template_name='accounts/login.html', context=context)

    def post(self, request):
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            messages.success(request, "شما با موافقیت وارد شدید!")
            # TODO: Log in!
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "فرم متعبر نیست!")
            return render(request=request,
                          template_name='accounts/login.html', context={'form': form})



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
