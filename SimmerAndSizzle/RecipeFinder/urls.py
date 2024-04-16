from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),

    # path("/about", views.about, name="about"),
    # path("/favourites", views.favourites, name="favourites"),
    path("/search", views.search, name="search"),

    path("/recipe/<int:id>", views.recipe, name="view_recipe"),
    # path("/cuisine/<int:id>", views.cuisine, name="view_cuisine"),
    # path("/ingredient/<int:id>", views.ingredient, name="view_ingredient"),

    # API
    path("/new_recipe", views.new_recipe, name="new_recipe"),
    path("/recipe/<int:id>/like", views.recipe, name="like_recipe"),
    path("/recipe/<int:id>/edit", views.recipe, name="edit_recipe"),
]