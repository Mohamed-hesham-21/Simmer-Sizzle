from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractUser):
    isAdmin = models.BooleanField(default=True)


class Cuisine(models.Model):
    name = models.CharField(max_length=100)
    info = models.TextField(max_length=1000)

    def __str__(self):
        return self.name
    
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    carbs = models.FloatField(null=True)
    protein = models.FloatField(null=True)
    fats = models.FloatField(null=True)

class Unit(models.Model):
    name = models.CharField(max_length=25, unique=True)
    conversion = models.FloatField(null=True)

def adminValidator(userID):
    user = User.objects.get(id=userID)
    if not user.isAdmin:
        raise ValidationError

class Recipe(models.Model):
    courses_pairs = [("Appetizers", "Appetizers"), ("Main Course", "Main Course"), ("Dessert", "Dessert")]
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="recipes", validators=[adminValidator])
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    course = models.CharField(max_length=25, choices=courses_pairs)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE, related_name="recipes")
    prepTime = models.IntegerField()
    cookTime = models.IntegerField()
    servings = models.IntegerField()
    image = models.ImageField(null=True, upload_to="images/")

    @classmethod
    def trending(cls):
        recipes = list(Recipe.objects.all())
        recipes.sort(key=lambda recipe: recipe.likesCount() / recipe.viewsCount())
        return recipes
    
    @classmethod
    def courses(cls):
        coursesList = []
        for course in cls.courses_pairs:
            coursesList.append(course[0])
        return coursesList

    def __str__(self):
        return self.name

    def totalTime(self):
        return self.prepTime + self.cookTime

    def carbs(self):
        total = 0
        for ing in self.ingredients.all():
            if not ing.ingredient.carbs or not ing.unit.conversion:
                return None
            total += ing.ingredient.carbs * ing.quantity * ing.unit.conversion
        return int(total)

    def fats(self):
        total = 0
        for ing in self.ingredients.all():
            if not ing.ingredient.fats or not ing.unit.conversion:
                return None
            total += ing.ingredient.fats * ing.quantity * ing.unit.conversion
        return int(total)
    
    def protein(self):
        total = 0
        for ing in self.ingredients.all():
            if not ing.ingredient.protein or not ing.unit.conversion:
                return None
            total += ing.ingredient.protein * ing.quantity * ing.unit.conversion
        return int(total)

    def calories(self):
        if not self.carbs() or not self.fats() or not self.protein():
            return None
        return self.carbs() * 4 + self.protein() * 4 + self.fats() * 9

    def recommendations(self):
        return Recipe.objects.filter(cuisine=self.cuisine).exclude(id=self.id).all()
    
    def checkLike(self, user):
        return True if user.likes.filter(recipe=self) else False

    def addView(self, user):
        if not self.views.filter(user=user):
            View.create(user, recipe)

    def viewsCount(self):
        return self.views.count()

    def likesCount(self):
        return self.likes.count()

    def getSteps(self):
        return self.steps.all().order_by("index")
    
    def getIngredients(self):
        ingredients = self.ingredients.all()
        for ing in ingredients:
            ing.name = ing.ingredient.name
            ing.unit = ing.ingredient.unit
        return ingredients

class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    content = models.CharField(max_length=200)
    index = models.IntegerField()

    def __str__(self):
        return f"{self.recipe.name}: {self.index} - {self.content}"

class HasIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipes")
    quantity = models.FloatField()
    unit = models.ForeignKey(Unit, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.recipe.name}: {self.quantity} {self.ingredient.unit} {self.ingredient.name}" 

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="likes")

class View(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="views")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="views")