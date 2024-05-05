import json
from django.contrib import auth
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
RECIPE_LIMIT = 10

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
            "carbs",
            "fats",
            "protein",
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

class NewIngredientForm(forms.ModelForm):
    class Meta:
        model = models.Ingredient
        fields = (
            "name",
        )

class NewStepForm(forms.ModelForm):
    class Meta:
        model = models.Step
        fields = (
            "name",
        )

class NewIngredientConForm(forms.ModelForm):
    class Meta:
        model = models.HasIngredient
        fields = (
            "ingredient",
            "quantity",
            "unit",
        )

def checkRequest(request, auth=True, post=True, admin=False):
    if post and request.method != "POST":
        return JsonResponse({"error": "Only post method is allowed."}, status=400)
    if auth and not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication error."}, status=401)
    if admin and not request.user.isAdmin:
        return JsonResponse({"error": "You're not an admin."}, status=403)
    return None

def checkFormErrors(form):
    errors = []
    for field in form:
        for error in field.errors:
            errors.append(f"{field.label}: {error}")
    return errors

def checkKeys(dic, keys):
    for key in keys:
        if dic.get(key) is None:
            return key

def checkLikes(user, recipes):
    if user.is_authenticated:
        for recipe in recipes:
            recipe.liked = recipe.checkLike(user)
    return recipes; 

def getPage(recipes, pageNum):
    if not len(recipes):
        return None
    recipes = recipes.order_by('-dateAdded')
    pag = Paginator(recipes, RECIPE_LIMIT)
    assert pageNum <= pag.num_pages
    return pag.page(pageNum).object_list

def cuisines(request):
    return JsonResponse({"cuisines": models.Cuisine.objects.all()})

def units(request):
    return JsonResponse({"units": models.Unit.objects.all()})

def courses(request):
    return JsonResponse({"courses": models.Recipe.courses()})

def index(request):
    return render(request, "RecipeFinder/index.html")

def login_view(request):
    return render(request, "RecipeFinder/login.html")

def register_view(request):
    return render(request, "RecipeFinder/register.html")

def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    response = checkRequest(request, auth=False)
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
    user = userForm.save(commit=False)
    user.set_password(userForm.cleaned_data["password"])
    user.save()
    auth.login(request, user)
    return JsonResponse({"success": "User authenticated successfully"}, status=200)

def login(request):
    response = checkRequest(request, auth=False)
    if response is not None:
        return response
    data = json.loads(request.body)
    missingKey = checkKeys(data, ["username", "password"])
    if missingKey is not None:
        return JsonResponse({"error": f"Missing {missingKey}."}, status=400)
    username = data["username"]
    password = data["password"]
    user = auth.authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid username and/or password."}, status=401)
    auth.login(request, user)
    return JsonResponse({"success": "User authenticated successfully"}, status=200)
      

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

def about_view(request):
    return render(request, "RecipeFinder/about.html")

def favourites_view(request):
    return render(request, "RecipeFinder/category.html")

def favourites(request):
    response = checkRequest(request, post=False)
    if response is not None:
        return response
    data = json.loads(request.body)
    recipes = models.Recipe.favourites(request.user)
    pageNum = data["page"] if data.get("page") else 1
    try:
        recipes = getPage(recipes, pageNum)
    except AssertionError:
        return JsonResponse({"error": "Page specified is not available"}, status=400)
    return JsonResponse({"recipes": recipes}, status=200)


def add_recipe_view(request):
    return render(request, "RecipeFinder/new_recipe.html", {
        "cuisines": models.Cuisine.objects.all(),
        "courses": models.Recipe.courses(),
        "units": models.Unit.objects.all(),
    })

def add_recipe(request):
    response = checkRequest(request, admin=True)
    if response is not None:
        return response
    data = json.loads(request.body)
    if not data.get("recipe"):
        return JsonResponse({"error": "Missing recipe."}, status=400)
    missingKey = checkKeys(data["recipe"], list(NewRecipeForm.Meta.fields) + ["ingredients", "steps"])
    if missingKey is not None:
        return JsonResponse({"error": f"Missing {missingKey}."}, status=400)

    recipeForm = NewRecipeForm(data["recipe"])
    if not recipeForm.is_valid():
        errors = checkFormErrors(recipeForm)
        return JsonResponse({"error": errors[0]}, status=400)
    recipe = recipeForm.save(commit=False)
    recipe.author = request.user
    ingredientList = []
    for ing in data["recipe"]["ingredients"]:
        name = ing["name"].strip().lower().capitalize()
        tempForm = NewIngredientForm(name)
        if not tempForm.is_valid():
            return JsonResponse({"error": "Ingrdient name is too long"}, status=400)
        
        ingredientList.append(name)
    

    for ing in data["ingredients"]:
        try:
            name = ing["name"].strip().lower().capitalize()
            if models.Ingredient.objects.filter(name=name) is not None:
                ingredient = models.Ingredient.objects.get(name=name)
            else:
                ingredient = models.Ingredient(name=name)
                ingredient.save()
            quantity = ing["quantity"]
            unit = Unit.objects.get(name=ing["unit"])
            newIngredient = HasIngredient(recipe, ingredient, quantity, unit)
            newIngredient.save()
        except Exception:
            recipe.delete()
            return JsonResponse({"error": "Invalid ingredient"}, status=400)
    
    # for index, step in enumerate(data["steps"]):
    #     try:
    #         content = step["content"]
    #         step = Step(recipe, content, index)
    #         step.save()
    #     except Exception:
    #         recipe.delete()
    #         return JsonResponse({"error": "Invalid step"}, status=400)
    recipe.save()
    return JsonResponse({"recipe_id": recipe.id}, status=200)

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