import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django import forms
from random import choice
from django.core.paginator import Paginator
from . import models
# Create your views here.

CATEGORY_LIMIT = 10

def template(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            return HttpResponseRedirect(reverse('index'))
    return wrapper

class NewRecipeForm(forms.ModelForm):
    class Meta:
        model = models.Recipe
        fields = (
            "name", 
            "description", 
            "course", 
            "cuisine", 
            "prepTime", 
            "cookTime", 
            "servings",
            )

class NewUserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = (
            "username",
            "email",
            "password",
            "isAdmin",
        )

class 


def checkRequest(request, auth=True, post=True):
    if post and request.method != "POST":
        return JsonResponse({"error": "Only post method is allowed."}, status=400)
    if auth and not request.user.is_authenticated():
        return JsonResponse({"error": "Authentication error."}, status=401)
    return None

def checkFormErrors(form):
    errors = []
    for field in form:
        errors += field.errors()
    return errors

def checkKeys(dic, keys):
    for key in keys:
        if dic.get(key) is None:
            return key


def login_view(request):
    return render(request, "RecipeFinder/login.html")

def register_view(request):
    return render(request, "RecipeFinder/register.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    response = checkRequest(request, False)
    if response is not None:
        return response
    data = json.loads(request.body)
    missingKey = checkKeys(data, NewUserForm.Meta.fields)
    if missingKey is not None:
        return JsonResponse({"error": f"Missing {missingKey}."}, status=400)

    if data["password"] != data["confirmation"]:
        return JsonResponse({"error": "Passwords don't match."}, status=400)

    userForm = NewUserForm(data)
    if not userForm.is_valid():
        errors = checkFormErrors(userForm)
        return JsonResponse({"error": errors[0]}, status=400)

    if models.User.objects.filter(username=data["username"]).exists():
        return JsonResponse({"error": "Username already taken."}, status=400)
    user = userForm.save()
    login(request, user)
    return JsonResponse({"success": "User authenticated successfully"}, status=200)

def login(request):
    response = checkRequest(request, False)
    if response is not None:
        return response
    data = json.loads(request.body)
    missingKey = checkKeys(data, ["username", "password"])
    if missingKey is not None:
        return JsonResponse({"error": f"Missing {missingKey}."}, status=400)
    username = data["username"]
    password = data["password"]
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid username and/or password."}, status=401)
    login(request, user)
    return JsonResponse({"success": "User authenticated successfully"}, status=200)


# def checkLikes(user, recipes):
#     if user.is_authenticated:
#         for recipe in recipes:
#             recipe.liked = recipe.checkLike(user)
#     return recipes;        

# # @template
# def index(request):
#     categories = [{
#         "name": "Trending",
#         "recipes": checkLikes(request.user, Recipe.trending()[: CATEGORY_LIMIT]),
#     }]
#     if Cuisine.objects.all():
#         cuisine = choice(list(Cuisine.objects.all()))
#         categories.append({
#             "name": cuisine.name,
#             "recipes": cuisine.recipes.all()[: CATEGORY_LIMIT],
#             })
#     return render(request, "index.html", {
#         "categories": categories,
#         "cuisines": Cuisine.objects.all(),
#     })

# def about(request):
#     return render(request, "about.html", {
#         "cuisines": Cuisine.objects.all(),
#     })

# @template
# @login_required(login_url='login')
# def favourites(request):
#     assert request.user.is_authenticated
#     likes = request.user.likes.all()
#     recipes = []
#     for like in likes:
#         recipe = like.recipe
#         recipe.liked = True
#         recipes.append(recipe)
#     category = {
#         "name": "Favourites",
#         "recipes": recipes,
#     }
#     return render(request, "category.html", {
#         "category": category,
#         "cuisines": Cuisine.objects.all(),
#     })

# def all_cuisines_view(request):
#     categories = []
#     for cuisine in Cuisine.objects.all():
#         category = {
#             "name": cuisine.name,
#             "recipes": cuisine.recipes.all()[: CATEGORY_LIMIT]
#         }
#         categories.append(category)
#     return render(request, "index.html", {
#         "header": "Cusines",
#         "categories": categories,
#         "cuisines": Cuisine.objects.all(),
#     })

# @template
# def cuisine_view(request, id):
#     cuisine = Cuisine.objects.get(id=id)
    
#     categories = []
#     for course in Recipe.courses():
#         category = {
#             "name": course,
#             "recipes": Cuisine.recipes.filter(course=course)[: CATEGORY_LIMIT],
#             "link": reverse("course", args=(cuisine.id, course))
#         }
#         categories.append(category)
    
#     linkHistory = [
#         {
#             "name": cuisine.name,
#             "ref": reverse("cuisine", args=(cuisine.id,))
#         }
#     ]

#     return render(request, "index.html", {
#         "linkHistory": linkHistory,
#         "header": cuisine.name,
#         "info": cuisine.info,
#         "categories": categories,
#         "cuisines": Cuisine.objects.all(),
#     })

# @template
# def course_view(request, id, course):
#     assert course in recipe.courses()
#     cuisine = Cuisine.objects.get(id=id)
#     category = {
#         "name": course,
#         "recipes": cuisine.recipes.filter(course=course),
#     }

#     linkHistory = [
#         {
#             "name": cuisine.name,
#             "ref": reverse("cuisine", args=(cuisine.id,)),
#         },
#         {
#             "name": course,
#             "ref": reverse("course", args=(cuisine.id, course)),
#         }
#     ]
#     return render(request, "category.html", {
#         "linkHistory": linkHistory,
#         "category": category,
#         "cuisines": Cuisine.objects.all(),
#     })


# def all_ingredients_view(request):
#     categories = []
#     for ingredient in Ingredient.objects.all():
#         category = {
#             "name": ingredient.name,
#             "recipes": ingredient.recipes.all()[: CATEGORY_LIMIT]
#         }
#         categories.append(category)
#     return render(request, "index.html", {
#         "header": "Ingredients",
#         "categories": categories,
#         "cuisines": Cuisine.objects.all(),
#     })

# def ingredient_view(request, id):
#     ingredient = Ingredient.objects.get(id=id)
    
#     category = {
#         "name": ingredient.name,
#         "recipes": ingredient.recipes.all(),
#     }
#     return render(request, "category.html", {
#         "category": category,
#         "cuisines": Cuisine.objects.all(),
#     })

# def all_recipe_view(request):
#     recipes = Recipe.trending()
#     checkLikes(recipes)
#     category = {
#         "name": "All recipes",
#         "recipes": recipes,
#     }
#     return render(request, "category.html", {
#         "category": category,
#         "cuisines": Cuisine.objects.all(),
#     })

# @template
# def recipe_view(request, id):
#     recipe = Recipe.objects.get(id=id)
#     if request.user.is_authenticated:
#         recipe.addView(request.user)
#     recipe.liked = recipe.checkLike(request.user)
#     linkHistory = [
#         {
#             "name": recipe.cuisine.name,
#             "ref": reverse("cuisine", args=(recipe.cuisine.id,))
#         },
#         {
#             "name": recipe.course,
#             "ref": reverse("course", args=(recipe.cuisine.id, recipe.course))
#         },
#         {
#             "name": recipe.name,
#             "ref": reverse("recipe", args=(recipe.id,))
#         }
#     ]
#     return render(request, "recipe.html", {
#         "linkHistory": linkHistory,
#         "recipe": recipe,
#         "cuisines": Cuisine.objects.all(),
#     })

# @login_required(login_url='login')
# def new_recipe_view(request):
#     assert request.user.isAdmin
#     return render(request, "new_recipe.html", {
#         "cuisines": Cuisine.objects.all(),
#         "courses": Recipe.courses(),
#         "units": Unit.objects.all(),
#     })

# @template
# def edit_recipe_view(request, id):
#     recipe = Recipe.objects.get(id=id)
#     assert recipe.author == request.user
#     return render(request, "new_recipe.html", {
#         "recipe": recipe,
#         "cuisines": Cuisine.objects.all(),
#         "courses": Recipe.courses(),
#         "units": Unit.objects.all(),
#     })

# def like_recipe(request, id):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid method. Only POST method is allowed."}, status=400)
#     if not request.user.is_authenticated:
#             return JsonResponse({"error": "Authentication error"}, status=401)
#     if not Recipe.objects.filter(id=id):
#         return JsonResponse({"error": "Recipe doesn't exist"}, status=400)
    
#     recipe = Recipe.objects.get(id=id)
#     if request.user.likes.filter(recipe=recipe):        
#         request.user.likes.get(recipe=recipe).delete()
#         return JsonResponse({"success": "Recipe removed from favourites successfully"}, status=200)
        
#     Like.objects.create(user=request.user, recipe=recipe)
#     return JsonResponse({"success": "Recipe added to favourites successfully"}, status=200)

# def add_recipe(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid method. Only POST method is allowed."}, status=400)
#     if not request.user.is_authenticated or not request.user.isAdmin:
#         return JsonResponse({"error": "Authentication error"}, status=401)
    
#     data = json.loads(request.body)

#     try:
#         recipeForm = NewRecipeForm(data)
        
#     except Exception:
#         return JsonResponse({"error": "some data missing"}, status=400)


#     if not recipeForm.is_valid():
#         errors = []
#         for field in recipeForm:
#             errors += field.errors()
#         return JsonResponse({"error": error[0]}, status=400)
    
#     recipe.save()
#     for ing in data["ingredients"]:
#         try:
#             name = ing["name"].strip().lower().capitalize()
#             if Ingredient.objects.filter(name=name):
#                 ingredient = Ingredient.objects.get(name=name)
#             else:
#                 ingredient = Ingredient(name=name)
#                 ingredient.save()        
#             quantity = ing["quantity"]
#             unit = Unit.objects.get(name=ing["unit"])
#             newIngredient = HasIngredient(recipe, ingredient, quantity, unit)
#             newIngredient.save()
#         except Exception:
#             recipe.delete()
#             return JsonResponse({"error": "Invalid ingredient"}, status=400)
    
#     for index, step in enumerate(data["steps"]):
#         try:
#             content = step["content"]
#             step = Step(recipe, content, index)
#             step.save()
#         except Exception:
#             recipe.delete()
#             return JsonResponse({"error": "Invalid step"}, status=400)
#     return JsonResponse({"recipe_id": recipe.id}, status=200)

# def edit_recipe(request, id):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid method. Only POST method is allowed."}, status=400)
#     if not request.user.is_authenticated or not request.user.isAdmin:
#         return JsonResponse({"error": "Authentication error"}, status=401)
#     if not Recipe.objects.filter(id=id):
#         return JsonResponse({"error": "Recipe doesn't exist"}, status=400)
    
#     recipe = Recipe.objects.get(id=id)
#     if recipe.author != request.user:
#         return JsonResponse({"error": "You can't edit a recipe you didn't create"}, status=403)
#     response = add_recipe(request)
#     if response.status_code == 200:
#         recipe.delete()
#         recipe = Recipe.objects.get(id=response.content["recipe_id"])
#         recipe.id = id
#         recipe.save()
#     return response

# def delete_recipe(request, id):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid method. Only POST method is allowed."}, status=400)
#     if not request.user.is_authenticated or not request.user.isAdmin:
#         return JsonResponse({"error": "Authentication error"}, status=401)
#     if not Recipe.objects.filter(id=id):
#         return JsonResponse({"error": "Recipe doesn't exist"}, status=400)
    
#     recipe = Recipe.objects.get(id=id)
#     if recipe.author != request.user:
#         return JsonResponse({"error": "You can't edit a recipe you didn't create"}, status=403)
#     recipe.delete()
#     return JsonResponse({"success": "Recipe removed successufully"}, status=200)