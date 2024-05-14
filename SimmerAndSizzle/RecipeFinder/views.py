import json
from django.templatetags.static import static
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

# Some decorators

def exception_handle(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            return HttpResponseRedirect(reverse('index'))
    return wrapper

def admin_required(fn):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.isAdmin:
            return fn(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('index'))
    return wrapper

# Forms to handle invalid data

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
            "quantity",
            "unit",
        )

class NewStepForm(forms.ModelForm):
    class Meta:
        model = models.Step
        fields = (
            "content",
        )

# Helper functions

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

def getRecipeCardList(recipes, user):
    recipeList = []
    for recipe in recipes:
        recipeList.append({
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "imageURL": recipe.image.url if recipe.image else static("RecipeFinder/food.jpg"),
            "liked": recipe.checkLike(user),
            "url": reverse("recipe", args=(recipe.id,))
        })
    return recipeList

def getRecipeFromRequest(request):
    data = json.loads(request.body)
    if not data.get("recipe"):
        return JsonResponse({"error": "Missing recipe."}, status=400)
    missingKey = checkKeys(data["recipe"], list(NewRecipeForm.Meta.fields) + ["ingredients", "steps"])
    if missingKey is not None:
        return JsonResponse({"error": f"Missing {missingKey}."}, status=400)

    # handing recipe image
    recipe = data["recipe"]
    recipe['image'];

    # done handling
    recipeForm = NewRecipeForm(data["recipe"])
    if not recipeForm.is_valid():
        return JsonResponse({"error": checkFormErrors(recipeForm)[0]}, status=400)


    recipe = recipeForm.save(commit=False)
    recipe.author = request.user
    ingredientList = []
    stepList = []

    for ing in data["recipe"]["ingredients"]:
        ing["name"] = ing["name"].strip().lower().capitalize()
        ingredientForm = NewIngredientForm(ing)
        if not ingredientForm.is_valid():
            return JsonResponse({"error": checkFormErrors(ingredientForm)[0]}, status=400)
        ingredient = ingredientForm.save(commit=False)
        ingredient.recipe = recipe
        ingredientList.append(ingredient)
    
    for index, step in enumerate(data["recipe"]["steps"]):
        step = {"content": step}
        stepForm = NewStepForm(step)
        if not stepForm.is_valid():
            return JsonResponse({"error": checkFormErrors(stepForm)[0]}, status=400)
        step = stepForm.save(commit=False)
        step.index = index
        step.recipe = recipe
        stepList.append(step)
    print(data["recipe"]["image"])
    return [recipe, ingredientList, stepList]

def getPage(items, pageNum, limit=RECIPE_LIMIT):
    assert len(items) > 0
    pag = Paginator(items, limit)
    assert pageNum <= pag.num_pages
    return pag.page(pageNum).object_list

def defaultContext(dic={}):
    dic["cuisines"] = models.Cuisine.objects.all()
    dic["courses"] = models.Recipe.courses()
    dic["units"] = models.Unit.objects.all()
    
    if dic.get("API"):
        dic["categories"] = []
        for category in dic["API"]:
            dic["categories"].append({
                "header": category["header"],
                "id": category["id"],
            })
            del category["header"]
        
    return dic;

def processQuery(allRecipes, query):
    recipes = models.Recipe.objects.none()
    recipes |= allRecipes.filter(name__contains=f"{query}")
    recipes |= allRecipes.filter(course__contains=f"{query}")
    for recipe in allRecipes.all():
        match = False
        if query in recipe.cuisine.name.lower():
            match = True
        for ingredient in recipe.ingredients.all():
            if query in ingredient.name.lower():
                match = True
        if match:
            recipes |= allRecipes.filter(id=recipe.id)
    return recipes

def getRecipeRecommendations(recipes, recipe):
    return recipes.filter(cuisine=recipe.cuisine, course=recipe.course).exclude(id=recipe.id)

def getPersonalizedRecommendations(recipes, user):
    allRecipes = []
    for view in user.views.order_by("-timestamp")[:10]:
        allRecipes += list(getRecipeRecommendations(recipes, view.recipe))
    
    return sorted(allRecipes, key=lambda recipe: allRecipes.count(recipe), reverse=True)

def getTrendingCuisine():
    cuisineViews = {}
    for view in models.View.objects.order_by("-timestamp")[:1000]:
        cuisineID = view.recipe.cuisine.id
        if not cuisineViews.get(cuisineID):
            cuisineViews[cuisineID] = 0
        cuisineViews[cuisineID] += 1
    trendingCuisine = None
    maxViews = 0
    for cuisine, views in cuisineViews.items():
        if views > maxViews:
            trendingCuisine = cuisine
    return models.Cuisine.objects.get(id=trendingCuisine) if trendingCuisine else None

def getFeed(user):
    API = []
    API.append({
        "header": "Trending",
        "request": {"order_by": "popularity"},
        "id": "trending-container",
    })
    cuisine = getTrendingCuisine()
    if cuisine:
        API.append({
            "header": cuisine.name,
            "request": {"cuisine": cuisine.id, "order_by": "popularity"},
            "id": f"trending-cuisine-{cuisine.name}",
        })
    if user.is_authenticated:
        API.append({
        "header": "Just for you",
        "request": {"personalized": 1},
        "id": f"personalized-container-{user.username}",
        })
    querySet = models.Cuisine.objects.all()
    if querySet.exists():
        cuisine = choice(list(querySet))
        course = choice(models.Recipe.courses())
        API.append({
            "header": f"Discover: {cuisine.name} {course}",
            "request": {"cusisine": 1, "course": course},
            "id": f"random-container-{cuisine.name}-{course}",
        })
    return API

# Views

def index(request):
    visited = request.session.get('visited', False)
    request.session["visited"] = True
    if not visited:
        return render(request, "RecipeFinder/home.html", defaultContext())
    return render(request, "RecipeFinder/index.html", defaultContext({
        "API": getFeed(request.user),
    }))

def login_view(request):
    return render(request, "RecipeFinder/login.html", defaultContext())

def register_view(request):
    return render(request, "RecipeFinder/register.html", defaultContext())

@login_required(login_url='login')
def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("index"))

def about_view(request):
    return render(request, "RecipeFinder/about.html", defaultContext())

def recipes_view(request):
    return render(request, "RecipeFinder/category.html", defaultContext({
        "API": [{
            "header": "All recipes",
            "request": {"order_by": "date_added",},
            "id": "all-recipes-container",
        }]
    }))

@login_required(login_url='login')
def favourites_view(request):
    return render(request, "RecipeFinder/category.html", defaultContext({
        "API": [{
            "header": "Favourites",
            "request": {"favourites": 1,},
            "id": "favourites-container",
        }]
    }))

@admin_required
def add_recipe_view(request):
    return render(request, "RecipeFinder/new_recipe.html", defaultContext())

@admin_required
def edit_recipe_view(request, id):
    return render(request, "RecipeFinder/edit_recipe.html", defaultContext({
        "recipe": models.Recipe.objects.get(id=id),
    }))

def cuisine_view(request, id):
    cuisine = models.Cuisine.objects.get(id=id)
    API = []
    for course in models.Recipe.courses():
        API.append({
            "header": course,
            "request": {
                "cuisine": id,
                "course": course
            },
            "id": f"{cuisine.name}-{course}-container",
            "url": reverse("course", args=(id, course)),
        })
    
    linkHistory = [
        {
            "name": cuisine.name,
            "ref": reverse("cuisine", args=(cuisine.id,))
        }
    ]

    return render(request, "RecipeFinder/index.html", {
        "linkHistory": linkHistory,
        "header": cuisine.name,
        "info": cuisine.info,
        "cuisines": models.Cuisine.objects.all(),
        "API": API,
    })

def course_view(request, id, course):
    assert course in models.Recipe.courses()
    cuisine = models.Cuisine.objects.get(id=id)

    linkHistory = [
        {
            "name": cuisine.name,
            "ref": reverse("cuisine", args=(cuisine.id,)),
        },
        {
            "name": course,
            "ref": reverse("course", args=(cuisine.id, course)),
        }
    ]
    return render(request, "RecipeFinder/category.html", defaultContext({
        "linkHistory": linkHistory,
        "API": [{
            "header": "",
            "request": {
                "cuisine": id,
                "course": course,
            },
            "id": f"{cuisine.name}-{course}-main-container",
            }]
    }))

def chef_view(request, username):
    user = models.User.objects.get(username=username)
    return render(request, "RecipeFinder/category.html", defaultContext({
        "API": [{
            "header": f"{user.username}'s recipes",
            "request": {"favourites": 1,},
            "id": "favourites-container",
        }]
    }))

def search_view(request):
    try:
        query = request.GET["q"];
        assert len(query) > 0;
    except Exception:
        return HttpResponseRedirect(reverse("index"));
    return render(request, "RecipeFinder/category.html", defaultContext({
        "past_query": query,
        "API": 
        [
            {
                "header": f"Search: {query}",
                "request": {
                    "query": query
                },
                "id": f"search-results-container",
            }
        ]
    }))

def recipe_view(request, id):
    recipe = models.Recipe.objects.get(id=id)
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
    return render(request, "RecipeFinder/recipe.html", defaultContext({
        "linkHistory": linkHistory,
        "recipe": recipe,
        "API": [{
            "header": "",
            "request": {
                "recipeToRecommend": id
            },
            "id": "recommendations-container"
            }],
    }))

# API

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

@csrf_exempt
def recipes(request):
    data = json.loads(request.body)
    recipes = models.Recipe.objects.all()
    if data.get("author"):
        if not models.User.objects.filter(username=data["author"]).exists():
            return JsonResponse({"error": "user not found"})
        recipes = recipes.filter(user=models.User.objects.get(username=data["author"]))
    if data.get("cuisine"):
        if not models.Cuisine.objects.filter(id=data["cuisine"]):
            return JsonResponse({"error": "cuisine doesn't exist"})
        recipes = recipes.filter(cuisine=models.Cuisine.objects.get(id=data["cuisine"]))
    if data.get("course"):
        if data["course"] not in models.Recipe.courses():
            return JsonResponse({"error": "course doesn't exist"})
        recipes = recipes.filter(course=data["course"])
    if data.get("recipeToRecommend"):
        try:
            recipe = models.Recipe.objects.get(id=data["recipeToRecommend"])
        except models.Recipe.DoesNotExist:
            return JsonResponse({"error": "Recipe doesn't exist"}, status=404)

        recipes = getRecipeRecommendations(recipes, recipe)

    if data.get("query"):
        recipes = processQuery(recipes, data["query"].strip().lower());

    recipeList = []
    if data.get("favourites"):
        response = checkRequest(request, post=False)
        if response is not None:
            return response
        for like in request.user.likes.order_by("-timestamp"):
            recipeList.append(like.recipe)
    elif data.get("personalized"):
        response = checkRequest(request, post=False)
        if response is not None:
            return response
        recipeList = list(getPersonalizedRecommendations(recipes, request.user))
    else:
        recipeList = list(recipes)

    
    if data.get("order_by") and data["order_by"] == "popularity":
        recipeList.sort(key=lambda recipe: recipe.popularityKey(), reverse=True)
    elif data.get("favourites") is None:
        recipeList.sort(key=lambda recipe: recipe.dateAdded, reverse=True)
    
    
    recipeList = getRecipeCardList(recipeList, request.user)
    pageNum = data["page"] if data.get("page") else 1
    try:
        recipeList = getPage(recipeList, pageNum)
    except AssertionError:
        return JsonResponse({"error": "Page doesn't exist"}, status=400)
    return JsonResponse({"recipeList": recipeList}, status=200)

@csrf_exempt
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

@csrf_exempt 
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

@csrf_exempt    
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

def units(request):
    units = []
    for unit in models.Unit.objects.all():
        units.append(unit.name)
    return JsonResponse({"units": units}, status=200)

def cuisines(request):
    cuisines = []
    for cuisine in models.Cuisine.objects.all():
        cuisines.append(cuisine.name)
    return JsonResponse({"cuisines": cuisines}, status=200)

def courses(request):
    return JsonResponse({"courses": models.Recipe.courses()}, status=200)