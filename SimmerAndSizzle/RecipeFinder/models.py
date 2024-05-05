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
    carbs = models.IntegerField(null=True)
    protein = models.IntegerField(null=True)
    fats = models.IntegerField(null=True)
    image = models.ImageField(null=True, upload_to="images/")
    dateAdded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @classmethod
    def trending(cls):
        recipes = list(Recipe.objects.all())
        recipes.sort(key=lambda recipe: recipe.likesCount() / recipe.viewsCount(), reverse=True)
        return recipes
    
    @classmethod
    def courses(cls):
        coursesList = []
        for course in cls.courses_pairs:
            coursesList.append(course[0])
        return coursesList

    @classmethod
    def favourites(cls, user):
        recipes = []
        for recipe in cls.objects.all():
            if recipe.checkLike(user):
                recipes.append(recipe)
        return recipes

    def totalTime(self):
        return self.prepTime + self.cookTime
    
    def calories(self):
        if not self.carbs or not self.fats or not self.protein:
            return 0
        return 4 * self.carbs + 4 * self.protein + 9 * self.fats

    def recommendations(self):
        return Recipe.objects.filter(cuisine=self.cuisine).exclude(id=self.id).all()
    
    def checkLike(self, user):
        return True if user.likes.filter(recipe=self) else False

    def addView(self, user):
        if self.views.filter(user=user) is None:
            View.objects.create(user, self)

    def like(self, user):
        if self.likes.filter(user) is None:
            Like.objects.create(user, self)
        else:
            self.likes.get(user=user).delete()

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
    timestamp = models.DateTimeField(auto_now_add=True)

class View(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="views")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="views")
    timestamp = models.DateTimeField(auto_now_add=True)