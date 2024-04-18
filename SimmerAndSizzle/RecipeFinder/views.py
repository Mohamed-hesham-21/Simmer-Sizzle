from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import User, Cuisine, Ingredient, Recipe, Step, HasIngredient, Like
# Create your views here.

def index(request):
    categories = [{
        "name": "All",
        "recipes": Recipe.objects.all(),
    }]
    return render(request, "index.html", {
        "categories": categories,
    })

def register_view(request):
    if request.method == "POST":
        if request.POST["password"] != request.POST["confirmation"]:
            return render(request, "login.html", {
            "msg": "Passwords must match."
        })
        try:
            if request.POST["is_admin"]:
                user = Admin.objects.create_user(username, email, password)
            else:
                user = User.objects.create_user(username, email, password)
            user.save()
        except Exception:
            return render(request, "register.html", {
                "msg": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
            
        return render(request, "login.html", {
            "msg": "Invalid username and/or password."
        })

    return render(request, "login.html")
    

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def recipe_view(request, id):
    recipe = Recipe.objects.get(id=id)
    return render(request, "recipe.html", {
        "recipe": recipe,
        "steps": recipe.steps.order_by('index'),
        "ingredients": recipe.ingredients.all(),
    })

def new_recipe(request):
    assert request.user.isAdmin
    return render(request, "new_recipe.html")

def about(request):
    return render(request, "about.html")

def favourites(request):
    assert request.user.is_authenticated
    likes = request.user.likes
    recipes = []
    for like in likes:
        recipes.append(like.recipe)
    categories = [{
        "name": "Favourites",
        "recipes": recipes,
    }]
    return render(request, "index.html", {
        "categories": categories,
    })
