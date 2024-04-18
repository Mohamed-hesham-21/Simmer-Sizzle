from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractUser):
    isAdmin = models.BooleanField(default=True)

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    def __str__(self):
        return self.image.name
class Cuisine(models.Model):
    name = models.CharField(max_length=100)
    info = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=25)
    carbs = models.FloatField()
    protein = models.FloatField()
    fats = models.FloatField()

    def calories(self):
        return self.carbs * 4 + self.protein * 4 + self.fats * 9
    
    def __str__(self):
        return self.name

def adminValidator(userID):
    user = User.objects.get(id=userID)
    if not user.isAdmin:
        raise ValidationError


class Recipe(models.Model):
    courses = [("Appetizers", "Appetizers"), ("Main Course", "Main Course"), ("Dessert", "Dessert")]
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="recipes", validators=[adminValidator])
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    course = models.CharField(max_length=25, choices=courses)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE, related_name="recipes")
    prepTime = models.IntegerField()
    cookTime = models.IntegerField()
    servings = models.IntegerField()
    image = models.ImageField(upload_to='images/' , null = True)
    

    def __str__(self):
        return self.name

    def totalTime(self):
        return self.prepTime + self.cookTime

    def calories(self):
        total = 0
        for ing in self.ingredients.all():
            total += ing.ingredient.calories() * ing.quantity
        return int(total)

    def carbs(self):
        total = 0
        for ing in self.ingredients.all():
            total += ing.ingredient.carbs * ing.quantity
        return int(total)

    def fats(self):
        total = 0
        for ing in self.ingredients.all():
            total += ing.ingredient.fats * ing.quantity
        return int(total)
    
    def protein(self):
        total = 0
        for ing in self.ingredients.all():
            total += ing.ingredient.protein * ing.quantity
        return int(total)
    def recommendations(self):
        return Recipe.objects.filter(cuisine=self.cuisine).exclude(id=self.id).all()

class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    content = models.CharField(max_length=200)
    index = models.IntegerField()

    def __str__(self):
        return f"{self.recipe.name}: {self.index} - {self.content}"

class HasIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipes")
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.recipe.name}: {self.quantity} {self.ingredient.unit} {self.ingredient.name}" 

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="likes")