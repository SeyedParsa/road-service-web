from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.views import View
from accounts.forms import SignUpForm, LoginForm, PasswordResetForm, NewPasswordForm


class PasswordResetComplete(View):
    def get(self, request):
        messages.success(request, "گذرواژه شما با موافقیت به‌روز شد!")
        return HttpResponseRedirect(reverse('accounts:login'))


class Logout(View):
    def get(self, request):
        logout(request)
        messages.success(request, "شما با موفقیت از اکانت خود خارج شدید!")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


# TODO: should be moved to core
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
<<<<<<< 9b69768459a0b83e5bf1fcbc89fc56b2cc0dbb08
        if request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        form = LoginForm()
=======
        # TODO: If logged in, redirect to LOGIN_REDIRECT_URL!
        form = AuthenticationForm()
>>>>>>> do basis of authentication logic
        context = {'form': form}
        return render(request=request,
                      template_name='accounts/login.html', context=context)

    def post(self, request):
<<<<<<< 9b69768459a0b83e5bf1fcbc89fc56b2cc0dbb08
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
=======
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            messages.success(request, "شما با موافقیت وارد شدید!")
            # TODO: Log in!
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "فرم متعبر نیست!")
            return render(request=request,
                          template_name='accounts/login.html', context={'form': form})

>>>>>>> do basis of authentication logic


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
