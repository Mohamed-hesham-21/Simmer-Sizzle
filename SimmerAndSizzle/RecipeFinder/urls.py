from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("new_recipe", views.new_recipe, name="new_recipe"),


    path("about", views.about, name="about"),
    path("favourites", views.favourites, name="favourites"),
    # path("search", views.search, name="search"),

    path("recipe/<int:id>", views.recipe_view, name="recipe"),
    path("cuisine/<int:id>", views.cuisine_view, name="cuisine"),
    path("cuisine/<int:id>/<str:course>", views.course_view, name="course"),

    # path("ingredient/<int:id>", views.ingredient_view, name="ingredient"),

    # API
    # path("add_recipe", views.add_recipe, name="add_recipe"),
    path("recipe/<int:id>/like", views.like_recipe, name="like_recipe"),
    # path("recipe/<int:id>/edit", views.recipe, name="edit_recipe"),
    # path("recipe/<int:id>/edit_image", views.recipe, name="edit_recipe"),
]