# Generated by Django 5.0.4 on 2024-05-07 13:39

import RecipeFinder.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("RecipeFinder", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ingredient",
            name="carbs",
        ),
        migrations.RemoveField(
            model_name="ingredient",
            name="fats",
        ),
        migrations.RemoveField(
            model_name="ingredient",
            name="name",
        ),
        migrations.RemoveField(
            model_name="ingredient",
            name="protein",
        ),
        migrations.AddField(
            model_name="ingredient",
            name="ingredient",
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ingredient",
            name="quantity",
            field=models.FloatField(
                default=1, validators=[RecipeFinder.models.nonNegative]
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ingredient",
            name="recipe",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredients",
                to="RecipeFinder.recipe",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ingredient",
            name="unit",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="RecipeFinder.unit",
            ),
        ),
        migrations.AlterField(
            model_name="cuisine",
            name="name",
            field=models.CharField(
                max_length=100,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[a-zA-Z]*$", "Only alphabetic letters are allowed."
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="carbs",
            field=models.IntegerField(
                null=True, validators=[RecipeFinder.models.nonNegative]
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="cookTime",
            field=models.IntegerField(validators=[RecipeFinder.models.nonNegative]),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="fats",
            field=models.IntegerField(
                null=True, validators=[RecipeFinder.models.nonNegative]
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="name",
            field=models.CharField(
                max_length=100,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[a-zA-Z]*$", "Only alphabetic letters are allowed."
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="prepTime",
            field=models.IntegerField(validators=[RecipeFinder.models.nonNegative]),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="protein",
            field=models.IntegerField(
                null=True, validators=[RecipeFinder.models.nonNegative]
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="servings",
            field=models.IntegerField(validators=[RecipeFinder.models.nonNegative]),
        ),
        migrations.AlterField(
            model_name="unit",
            name="conversion",
            field=models.FloatField(
                null=True, validators=[RecipeFinder.models.nonNegative]
            ),
        ),
        migrations.AlterField(
            model_name="unit",
            name="name",
            field=models.CharField(
                max_length=25,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[a-zA-Z]*$", "Only alphabetic letters are allowed."
                    )
                ],
            ),
        ),
        migrations.DeleteModel(
            name="HasIngredient",
        ),
    ]
