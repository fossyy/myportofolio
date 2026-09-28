import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

from main.context import PORTFOLIO_PROFILE


def show_main(request):
    return render(request, "index.html", {
        "profile": PORTFOLIO_PROFILE,
        "last_login": request.COOKIES.get(
            "last_login", "No active login session / Cookie not found"
        ),
    })


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("main:login")
    return render(request, "register.html", {
        "name": PORTFOLIO_PROFILE["name"],
        "profile": PORTFOLIO_PROFILE,
        "form": form,
    })


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return response
    return render(request, "login.html", {
        "name": PORTFOLIO_PROFILE["name"],
        "profile": PORTFOLIO_PROFILE,
        "form": form,
    })


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response
