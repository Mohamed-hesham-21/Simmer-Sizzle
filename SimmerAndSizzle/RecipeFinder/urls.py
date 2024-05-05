from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),

    path("about", views.about_view, name="about"),
    path("favourites", views.favourites_view, name="favourites"),

    path("add_recipe", views.add_recipe_view, name="add_recipe"),

    # path("search", views.search, name="search"),

    # path("recipes", views.all_recipe_view, name="recipes"),
    # path("recipes/<int:id>", views.recipe_view, name="recipe"),
    # path("recipe/<int:id>/edit", views.edit_recipe_view, name="edit_recipe"),
    # path("cuisines", views.all_cuisines_view, name="cuisines"),
    # path("cuisines/<int:id>", views.cuisine_view, name="cuisine"),
    # path("cuisines/<int:id>/<str:course>", views.course_view, name="course"),
    # path("ingredients", views.all_ingredients_view, name="ingredients"),
    # path("ingredients/<str:ing>", views.ingredient_view, name="ingredient"),

    # API
    path("api/login", views.login),
    path("api/register", views.register),
    path("api/favourites", views.favourites),
    # path("api/add_recipe", views.add_recipe),
    # path("api/recipes", views.recipes),
    # path("api/recipes/<int:id>/recommendations", views.like_recipe),
    # path("api/recipes/<int:id>/like", views.like_recipe),
    # path("api/recipes/<int:id>/edit", views.edit_recipe),
    # path("api/recipes/<int:id>/delete", views.delete_recipe),
    # path("api/cuisines", views.cuisines),
    # path("api/ingredients", views.ingredients),
    # path("api/search", views.ingredient),
]