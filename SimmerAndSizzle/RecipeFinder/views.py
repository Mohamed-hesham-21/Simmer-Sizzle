import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from .models import User, Cuisine, Ingredient, Recipe, Step, HasIngredient, Like
# Create your views here.

def template(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            return HttpResponseRedirect(reverse('index'))
    return wrapper

# @template
def register_view(request):
    if request.method == "POST":
        if request.POST["password"] != request.POST["confirmation"]:
            return render(request, "login.html", {
            "msg": "Passwords must match."
        })
        # try:
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        isAdmin = (request.POST["is_admin"] == 'on')
        user = User(username=username, email=email, password=password, isAdmin=isAdmin)
        user.save()
        # except Exception:
        #     return render(request, "register.html", {
        #         "msg": "Username already taken."
        #     })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "register.html", {
        "cuisines": Cuisine.objects.all(),
    })

@template
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

    return render(request, "login.html", {
        "cuisines": Cuisine.objects.all(),
    })

@template
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def checkLikes(user, recipes):
    if user.is_authenticated:
        for recipe in recipes:
            recipe.liked = recipe.checkLike(user)
    return recipes;        

@template
def index(request):
    recipes = checkLikes(request.user, Recipe.objects.all());
    categories = [{
        "name": "All",
        "recipes": recipes,
    }]
    return render(request, "index.html", {
        "categories": categories,
        "cuisines": Cuisine.objects.all(),
    })

@template
@login_required(login_url='login')
def favourites(request):
    assert request.user.is_authenticated
    likes = request.user.likes.all()
    recipes = []
    for like in likes:
        recipe = like.recipe
        recipe.liked = True
        recipes.append(recipe)
    category = {
        "name": "Favourites",
        "recipes": recipes,
    }
    return render(request, "category.html", {
        "category": category,
        "cuisines": Cuisine.objects.all(),
    })

@template
def cuisine_view(request, id):
    cuisine = Cuisine.objects.get(id=id)
    
    categories = []
    for course in Recipe.courses:
        course = course[0]
        category = {
            "name": course,
            "recipes": Recipe.objects.filter(cuisine=cuisine, course=course),
            "link": reverse("course", args=(cuisine.id, course))
        }
        categories.append(category)
    
    linkHistory = [
        {
            "name": cuisine.name,
            "ref": reverse("cuisine", args=(cuisine.id,))
        }
    ]

    return render(request, "index.html", {
        "linkHistory": linkHistory,
        "header": cuisine.name,
        "info": cuisine.info,
        "categories": categories,
        "cuisines": Cuisine.objects.all(),
    })

@template
def course_view(request, id, course):
    cuisine = Cuisine.objects.get(id=id)
    category = {
        "name": course,
        "recipes": Recipe.objects.filter(cuisine=cuisine, course=course),
    }

    linkHistory = [
        {
            "name": cuisine.name,
            "ref": reverse("cuisine", args=(cuisine.id,))
        },
        {
            "name": course,
            "ref": reverse("course", args=(cuisine.id, course))
        }
    ]
    return render(request, "category.html", {
        "linkHistory": linkHistory,
        "category": category,
        "cuisines": Cuisine.objects.all(),
    })

@template
def recipe_view(request, id):
    recipe = Recipe.objects.get(id=id)
    if request.user.is_authenticated:
        recipe.addView(request.user)
    recipe.liked = recipe.checkLike(request.user)
    linkHistory = [
        {
            "name": recipe.cuisine.name,
            "ref": reverse("cuisine", args=(recipe.cuisine.id,))
        },
        {
            "name": recipe.course,
            "ref": reverse("course", args=(recipe.cuisine.id, recipe.course))
        },
        {
            "name": recipe.name,
            "ref": reverse("recipe", args=(recipe.id,))
        }
    ]
    return render(request, "recipe.html", {
        "linkHistory": linkHistory,
        "recipe": recipe,
        "steps": recipe.steps.order_by('index'),
        "ingredients": recipe.ingredients.all(),
        "cuisines": Cuisine.objects.all(),
    })

@login_required(login_url='login')
def new_recipe(request):
    assert request.user.isAdmin
    return render(request, "new_recipe.html", {
        "cuisines": Cuisine.objects.all(),
    })

def about(request):
    return render(request, "about.html", {
        "cuisines": Cuisine.objects.all(),
    })

def like_recipe(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method. Only POST method is allowed."}, status=400)
    if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication error"}, status=401)
    if not Recipe.objects.filter(id=id):
        return JsonResponse({"error": "Recipe doesn't exist"}, status=400)
    
    recipe = Recipe.objects.get(id=id)
    if request.user.likes.filter(recipe=recipe):        
        request.user.likes.get(recipe=recipe).delete()
        return JsonResponse({"success": "Recipe removed from favourites successfully"}, status=200)
        
    Like.objects.create(user=request.user, recipe=recipe)
    return JsonResponse({"success": "Recipe added to favourites successfully"}, status=200)

def add_recipe(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method. Only POST method is allowed."}, status=400)
    if not request.user.is_authenticated or not request.user.isAdmin:
            return JsonResponse({"error": "Authentication error"}, status=401)
    ingredients = []
    data = json.loads(request.body)

    recipe = Recipe

    for ing in data["ingredients"]:
        name = ing["name"].strip().lower().capitalize()
        if Ingredient.objects.filter(name=name):
            ingredient = Ingredient.objects.get(name=name)
        else:
            ingredient = Ingredient(name=name)
            ingredient.save()        
        quantity = ing["quantity"]
        unit = Unit.objects.get(id=ing["unit"])
        newIngredient = HasIngredient()