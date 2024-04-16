from django.contrib import admin
from .models import User, Cuisine, Ingredient, Course, Recipe, HasStep, HasIngredient, Like

# Register your models here.
admin.site.register(User)
admin.site.register(Cuisine)
admin.site.register(Ingredient)
admin.site.register(Course)
admin.site.register(Recipe)
admin.site.register(HasStep)
admin.site.register(HasIngredient)
admin.site.register(Like)


