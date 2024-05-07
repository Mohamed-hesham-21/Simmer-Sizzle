import json
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django import forms
from random import choice
from django.core.paginator import Paginator
from . import models
# Create your views here.

CATEGORY_LIMIT = 3
RECIPE_PER_CATEGORY_LIMIT = 10
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
            "ingredient",
            "quantity",
            "unit",
        )

class NewStepForm(forms.ModelForm):
    class Meta:
        model = models.Step
        fields = (
            "content",
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

def getRecipeCardList(recipes):
    recipeList = []
    for recipe in recipes:
        recipeList.append({
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "imageURL": recipe.image.url if recipe.image else None
        })
    return recipeList

def getRecipeFromRequest(request):
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
    stepList = []

    for ing in data["recipe"]["ingredients"]:
        ing["ingredient"] = ing["ingredient"].strip().lower().capitalize()
        ingredientForm = NewIngredientForm(ing)
        if not ingredientForm.is_valid():
            return JsonResponse({"error": checkFormErrors(ingredientForm)[0]}, status=400)
        ingredient = ingredientForm.save(commit=False)
        ingredient.recipe = recipe
        ingredientList.append(ingredient)
    
    for index, step in enumerate(data["recipe"]["steps"]):
        stepForm = NewStepForm(step)
        if not stepForm.is_valid():
            return JsonResponse({"error": checkFormErrors(stepForm)[0]}, status=400)
        step = stepForm.save(commit=False)
        step.index = index
        step.recipe = recipe
        stepList.append(step)

    return [recipe, ingredientList, stepList]

def getPage(items, pageNum, limit=RECIPE_LIMIT):
    if not len(recipes):
        return []
    pag = Paginator(items, limit)
    assert pageNum <= pag.num_pages
    return pag.page(pageNum).object_list

def index(request):
    return render(request, "RecipeFinder/index.html")

def login_view(request):
    return render(request, "RecipeFinder/login.html")

def register_view(request):
    return render(request, "RecipeFinder/register.html")

def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("index"))

def about_view(request):
    return render(request, "RecipeFinder/about.html")

def favourites_view(request):
    return render(request, "RecipeFinder/category.html")

def favourites(request):
    response = checkRequest(request, post=False)
    if response is not None:
        return response
    recipeList = getRecipeCardList(recipes)
    pageNum = request.GET["page"] if request.GET.get("page") else 1
    try:
        recipeList = getPage(recipeList, pageNum)
    except AssertionError:
        return JsonResponse({"error": "Page doesn't exist"})
    return JsonResponse({"recipes": recipeList}, status=200)


def add_recipe_view(request):
    return render(request, "RecipeFinder/new_recipe.html", {
        "cuisines": models.Cuisine.objects.all(),
        "courses": models.Recipe.courses(),
        "units": models.Unit.objects.all(),
    })

@csrf_exempt
def register(request):
    response = checkRequest(request, auth=False)
    if response is not None:
        return response
    data = json.loads(request.body)
    missingKey = checkKeys(data, list(NewUserForm.Meta.fields) + ["confirmation"])
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

@csrf_exempt
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

@csrf_exempt
def add_recipe(request):
    response = checkRequest(request, admin=False)
    if response is not None:
        return response
    response = getRecipeFromRequest(request)
    if isinstance(response, JsonResponse):
        return response
    recipe, ingredientList, stepList = response
    recipe.save()
    for ingredient in ingredientList:
        ingredient.save()
    for step in stepList:
        step.save()
    return JsonResponse({"recipe_id": recipe.id}, status=200)


def recipes(request):
    data = json.loads(request.body)
    recipes = models.Recipe.objects.all()
    if data.get("auther"):
        if not models.User.filter(username=data["auther"]).exists():
            return JsonResponse({"error": "user not found"})
        recipes = recipes.filter(user=models.User.get(username=data["auther"]))
    if data.get("cuisine"):
        if not models.Cuisine.objects.filter(name=data["cuisine"]):
            return JsonResponse({"error": "cuisine doesn't exist"})
        recipes = recipes.filter(cuisine=models.Cuisine.get(username=data["cuisine"]))
    if data.get("course"):
        if data["course"] not in models.Recipe.courses():
            return JsonResponse({"error": "course doesn't exist"})
        recipes = recipes.filter(course=data["course"])

    recipeList = getRecipeCardList(recipes)
    pageNum = request.GET["page"] if request.GET.get("page") else 1
    try:
        recipeList = getPage(recipeList, pageNum)
    except AssertionError:
        return JsonResponse({"error": "Page doesn't exist"})
    return JsonResponse({"recipes": recipeList}, status=200)
    
def recommendations(request, id):
    try:
        recipe = models.Recipe.objects.get(id=id)
    except models.Recipe.DoesNotExist:
        return JsonResponse({"error": "Recipe doesn't exist"}, status=404)

    # same cuisine , exclude the recipe itself
    recommended_recipes = models.Recipe.objects.filter(cuisine=recipe.cuisine, course=recipe.course).exclude(id=id)

    if not recommended_recipes:
        recommended_recipes = models.Recipe.objects.all()

    # Sort recommended recipes by likes count in descending order
    recommended_recipes = recommended_recipes.order_by('-likesCount')[:5]

    return JsonResponse({"recipeList": getRecipeCardList(recommended_recipes)}, status=200)

def search(request):
    query = request.GET["q"].lower()
    recipes = models.Recipe.objects.none()
    recipes |= models.Recipe.objects.filter(name__contains=f"%{query}%")
    recipes |= models.Recipe.objects.filter(course__contains=f"%{query}%")
    for recipe in models.Recipe.objects.all():
        match = False
        if query in recipe.cuisine.name.lower():
            match = True
        for ingredient in recipe.ingredients.all():
            if query in ingredient.ingredient.lower():
                match = True
        if match:
            recipes |= models.Recipe.objects.filter(id=recipe.id)
    recipeList = getRecipeCardList(recipes)
    pageNum = request.GET["page"] if request.GET.get("page") else 1
    try:
        recipeList = getPage(recipeList, pageNum)
    except AssertionError:
        return JsonResponse({"error": "Page doesn't exist"})
    return JsonResponse({"recipes": recipeList}, status=200)

def like_recipe(request, id):
    response = checkRequest(request)
    if response is not None:
        return response
    if not models.Recipe.objects.filter(id=id):
        return JsonResponse({"error": "Recipe doesn't exist"}, status=400)
    
    recipe = models.Recipe.objects.get(id=id)
    if recipe.checkLike(request.user):        
        request.user.likes.get(recipe=recipe).delete()
        return JsonResponse({"success": "Recipe removed from favourites successfully"}, status=200)
        
    models.Like.objects.create(user=request.user, recipe=recipe)
    return JsonResponse({"success": "Recipe added to favourites successfully"}, status=200)



def edit_recipe(request, id):
    response = checkRequest(request, admin=False)
    if response is not None:
        return response
    
    if not models.Recipe.objects.filter(id=id):
        return JsonResponse({"error": "Recipe doesn't exist"}, status=400)
    
    oldRecipe = models.Recipe.objects.get(id=id)
    response = getRecipeFromRequest(request)
    if isinstance(response, JsonResponse):
        return response
    recipe, ingredientList, stepList = response
    oldRecipe.delete()
    recipe.id = id
    recipe.save()
    for ingredient in ingredientList:
        ingredient.save()
    for step in stepList:
        step.save()
    return JsonResponse({"recipe_id": recipe.id}, status=200)

def delete_recipe(request, id):
    response = checkRequest(request, admin=True)
    if response is not None:
        return response
    if not models.Recipe.objects.filter(id=id):
        return JsonResponse({"error": "Recipe doesn't exist"}, status=400)
    
    recipe = models.Recipe.objects.get(id=id)
    # if recipe.author != request.user:
    #     return JsonResponse({"error": "You can't delete a recipe you didn't create"}, status=403)
    recipe.delete()
    return JsonResponse({"success": "Recipe removed successufully"}, status=200)

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
