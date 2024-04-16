from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Cuisine(models.Model):
    name = models.CharField(max_length=100)
    info = models.TextField(max_length=1000)

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=25)
    carbs = models.FloatField()
    protein = models.FloatField()
    fats = models.FloatField()

    def calories(self):
        return self.carbs * 4 + self.protein * 4 + self.fats * 9

class Course(models.Model):
    courses = [("Appetizers", "Appetizers"), ("Main Course", "Main Course"), ("Dessert", "Dessert")]
    name = models.CharField(max_length=25, choices=courses)

class Recipe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="recipes")
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE, related_name="recipes")
    prepTime = models.IntegerField()
    cookTime = models.IntegerField()
    servings = models.IntegerField()

    def calories(self):
        total = 0
        for ing in self.ingredients.all:
            total += ing.calories() * ing.quantity
        return total

    def carbs(self):
        total = 0
        for ing in self.ingredients.all:
            total += ing.carbs * ing.quantity
        return total

    def fats(self):
        total = 0
        for ing in self.ingredients.all:
            total += ing.fats * ing.quantity
        return total
    
    def protein(self):
        total = 0
        for ing in self.ingredients.all:
            total += ing.protein * ing.quantity
        return total

class HasStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)

class HasIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipes")
    quantity = models.IntegerField()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="likes")