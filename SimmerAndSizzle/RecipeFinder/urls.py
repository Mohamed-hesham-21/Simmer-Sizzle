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

    path("recipes", views.recipes_view, name="recipes"),
    path("recipes/<int:id>", views.recipe_view, name="recipe"),
    path("recipes/<int:id>/edit", views.edit_recipe_view, name="edit_recipe"),
    path("cuisines/<int:id>", views.cuisine_view, name="cuisine"),
    path("cuisines/<int:id>/<str:course>", views.course_view, name="course"),

    # API
    path("api/login", views.login, name="login_api"),
    path("api/register", views.register, name="register_api"),
    path("api/add_recipe", views.add_recipe, name="add_recipe.api"),
    path("api/recipes", views.recipes, name="recipes_api"),
    path("api/recipes/<int:id>/like", views.like_recipe, name="like_recipe_api"),
    path("api/recipes/<int:id>/edit", views.edit_recipe, name="edit_recipe_api"),
    path("api/recipes/<int:id>/delete", views.delete_recipe, name="delete_recipe_api"),
    path("api/search", views.search, name="search_api"),
    path("api/units", views.units),
    path("api/cuisines", views.units),
    path("api/courses", views.units),
]