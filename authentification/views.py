from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def home(request):
   message = ""
   if request.method == "POST":
      username = request.POST["username"]
      password = request.POST["password"]
      user = authenticate(request, username=username, password=password)
      if user is not None:
         login(request, user)
         return redirect("dashboard")
      else:
         message="Le nom d'utilisateur ou le mot de passe est incorrect."
   return render(request,'authentification/home.html', context={'message':message})

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')