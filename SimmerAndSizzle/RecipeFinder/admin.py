from django.contrib import admin
from .models import User, Cuisine, Ingredient, Unit, Recipe, Step, Like, View

# Register your models here.
admin.site.register(User)
admin.site.register(Cuisine)
admin.site.register(Ingredient)
admin.site.register(Unit)
admin.site.register(Recipe)
admin.site.register(Step)
admin.site.register(Like)
admin.site.register(View)